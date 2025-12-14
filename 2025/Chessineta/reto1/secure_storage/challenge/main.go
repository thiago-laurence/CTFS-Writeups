package main

import (
	"context"
	"crypto/rand"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"html"
	"io"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"regexp"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

const (
	cookieName     = "sid"
	maxUploadBytes = 10 << 20 // 10 MiB per file
	keySize        = 64
	dbPath         = "app.db"
)

type Server struct {
	db *sql.DB
}

func main() {
	db, err := initDB(dbPath)
	if err != nil {
		log.Fatalf("init db: %v", err)
	}
	defer db.Close()

	s := &Server{db: db}

	mux := http.NewServeMux()
	mux.HandleFunc("GET /", s.handleIndex)
	mux.HandleFunc("GET /logo.png", s.handleLogo)
	mux.HandleFunc("POST /upload", s.handleUpload)
	mux.HandleFunc("GET /download/{file}", s.handleDownload)

	addr := ":8080"
	log.Printf("listening on %s", addr)
	srv := &http.Server{
		Addr:              addr,
		Handler:           withCommonHeaders(mux),
		ReadTimeout:       30 * time.Second,
		WriteTimeout:      120 * time.Second,
		ReadHeaderTimeout: 10 * time.Second,
		IdleTimeout:       120 * time.Second,
	}
	if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
		log.Fatalf("server: %v", err)
	}
}

func withCommonHeaders(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Referrer-Policy", "no-referrer")
		w.Header().Set("Content-Security-Policy", "default-src 'self'; style-src 'unsafe-inline'")
		next.ServeHTTP(w, r)
	})
}

func initDB(path string) (*sql.DB, error) {
	// mattn/go-sqlite3 DSN: use _busy_timeout and _journal_mode params
	// See README for other options.
	dsn := fmt.Sprintf("file:%s?cache=shared&_busy_timeout=10000&_journal_mode=WAL", path)
	db, err := sql.Open("sqlite3", dsn)
	if err != nil {
		return nil, err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	schema := `
CREATE TABLE IF NOT EXISTS sessions (
  session_id TEXT PRIMARY KEY,
  dir TEXT NOT NULL,
  key BLOB NOT NULL
);
`
	if _, err := db.ExecContext(ctx, schema); err != nil {
		return nil, err
	}
	return db, nil
}

func (s *Server) handleIndex(w http.ResponseWriter, r *http.Request) {
	dir, _, err := s.getOrCreateSession(w, r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	entries, err := os.ReadDir(dir)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Build an HTML list with download links
	var listBuilder strings.Builder
	listBuilder.WriteString("<ul>")
	if len(entries) == 0 {
		listBuilder.WriteString("<li><em>(no files yet)</em></li>")
	} else {
		for _, entry := range entries {
			name := entry.Name()
			escaped := html.EscapeString(name)
			listBuilder.WriteString(`<li><code>`)
			listBuilder.WriteString(escaped)
			listBuilder.WriteString(`</code> <a href="/download/`)
			listBuilder.WriteString(escaped)
			listBuilder.WriteString(`">download</a></li>`)
		}
	}
	listBuilder.WriteString("</ul>")

	html := `<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Secure Storage</title>
<style>
/* ====== Theme & Resets ====== */
:root {
    --bg-start: #f7fafc;
    --bg-end: #eef2ff;
    --card-bg: #ffffff;
    --text: #0f172a;
    --muted: #6b7280;
    --border: #e5e7eb;
    --ring: #6366f1;
    --accent: #4f46e5;
    --accent-2: #22d3ee;
    --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-start: #0b1220;
        --bg-end: #111827;
        --card-bg: #0f172a;
        --text: #e5e7eb;
        --muted: #94a3b8;
        --border: #1f2937;
        --ring: #818cf8;
        --accent: #818cf8;
        --accent-2: #22d3ee;
        --shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }
}

* {
    box-sizing: border-box;
}
html,
body {
    height: 100%;
}

body {
    font-family:
        system-ui,
        -apple-system,
        Segoe UI,
        Roboto,
        Inter,
        Arial,
        sans-serif;
    color: var(--text);
    line-height: 1.6;
    margin: 0;
    background:
        radial-gradient(
            1200px 600px at 10% -10%,
            rgba(79, 70, 229, 0.12),
            transparent 60%
        ),
        radial-gradient(
            1200px 600px at 110% 10%,
            rgba(34, 211, 238, 0.12),
            transparent 60%
        ),
        linear-gradient(180deg, var(--bg-start), var(--bg-end));
    max-width: 760px;
    padding: 0 1rem;
    margin: 3rem auto;
}

/* ====== Card ====== */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.25rem;
    box-shadow: var(--shadow);
    backdrop-filter: saturate(120%) blur(6px);
    animation: pop 0.35s ease-out;
}

@keyframes pop {
    from {
        transform: translateY(6px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

h1 {
    margin: 0 0 0.75rem 0;
    font-size: clamp(1.4rem, 2.5vw, 1.9rem);
    letter-spacing: -0.02em;
}

/* ====== Typography ====== */
p {
    margin: 0.5rem 0 1rem;
    color: var(--muted);
}
h3 {
    margin: 1.25rem 0 0.5rem;
    font-size: 1rem;
    letter-spacing: 0.02em;
}

/* ====== Form & Inputs ====== */
form {
    display: grid;
    gap: 0.75rem;
}

label {
    display: block;
    font-weight: 600;
    color: var(--text);
    margin: 0.25rem 0;
}

input[type="file"] {
    display: block;
    width: 100%;
    padding: 0.6rem 0.75rem;
    border: 1px dashed var(--border);
    border-radius: 12px;
    background: transparent;
    color: var(--muted);
    transition:
        border-color 0.2s ease,
        background-color 0.2s ease;
}

input[type="file"]:hover {
    border-color: color-mix(in srgb, var(--ring) 40%, var(--border));
    background-color: color-mix(in srgb, var(--ring) 6%, transparent);
}

input[type="file"]::file-selector-button {
    margin-right: 0.75rem;
    padding: 0.45rem 0.8rem;
    border: 1px solid var(--border);
    border-radius: 10px;
    background: linear-gradient(180deg, #fff, #f6f7fb);
    color: var(--text);
    cursor: pointer;
    transition:
        transform 0.06s ease,
        border-color 0.2s ease;
}

@media (prefers-color-scheme: dark) {
    input[type="file"]::file-selector-button {
        background: linear-gradient(180deg, #0f172a, #0b1220);
        color: var(--text);
    }
}

input[type="file"]::file-selector-button:hover {
    border-color: color-mix(in srgb, var(--ring) 40%, var(--border));
    transform: translateY(-1px);
}

button {
    align-self: start;
    padding: 0.6rem 1rem;
    border-radius: 12px;
    border: 1px solid transparent;
    cursor: pointer;
    font-weight: 600;
    letter-spacing: 0.01em;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: #fff;
    box-shadow: 0 6px 18px rgba(79, 70, 229, 0.25);
    transition:
        transform 0.06s ease,
        box-shadow 0.2s ease,
        filter 0.2s ease;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 26px rgba(79, 70, 229, 0.33);
    filter: saturate(110%);
}

button:active {
    transform: translateY(0);
}

button:focus-visible,
input[type="file"]:focus-visible {
    outline: none;
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--ring) 25%, transparent);
}

/* ====== Links ====== */
a {
    color: var(--accent);
    text-decoration: none;
    border-bottom: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
    transition:
        color 0.15s ease,
        border-color 0.15s ease;
}
a:hover {
    color: color-mix(in srgb, var(--accent) 80%, var(--accent-2));
    border-color: currentColor;
}

/* ====== Lists (for listBuilder) ====== */
ul {
    list-style: none;
    margin: 0.5rem 0 0;
    padding: 0;
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 0.65rem 0.9rem;
    border-top: 1px solid var(--border);
    transition: background-color 0.15s ease;
}
li:first-child {
    border-top: 0;
}
li:hover {
    background: color-mix(in srgb, var(--ring) 6%, transparent);
}

/* Keep filenames readable */
code {
    background: color-mix(in srgb, var(--border) 60%, transparent);
    padding: 0.15rem 0.45rem;
    border-radius: 8px;
    font-family:
        ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono",
        monospace;
    font-size: 0.95em;
    color: var(--text);
}

/* ====== Small screens ====== */
@media (max-width: 520px) {
    body {
        margin: 2rem auto;
    }
    .card {
        padding: 1rem;
    }
    li {
        flex-direction: column;
        align-items: flex-start;
    }
    button {
        width: 100%;
    }
}
</style>
</head>
<body>
  <div class="card">
    <div style="text-align: center; margin-bottom: 1rem;">
       <img src="/logo.png" alt="Secure Storage Logo" style="max-width: 450px; height: auto;">
    </div>
    <p>Your session directory: <code>` + html.EscapeString(dir) + `</code></p>
    <form action="/upload" method="post" enctype="multipart/form-data">
      <label>Choose files (you can select multiple):
        <input type="file" name="file" multiple required>
      </label>
      <button type="submit">Upload & Encrypt</button>
    </form>
    <h3>Files (stored encrypted)</h3>
    ` + listBuilder.String() + `
  </div>
</body>
</html>`
	w.Header().Set("Content-Type", "text/html; charset=utf-8")
	_, _ = w.Write([]byte(html))
}

func (s *Server) handleUpload(w http.ResponseWriter, r *http.Request) {
	dir, key, err := s.getOrCreateSession(w, r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	r.Body = http.MaxBytesReader(w, r.Body, maxUploadBytes)

	if err := r.ParseMultipartForm(maxUploadBytes); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	form := r.MultipartForm
	if form == nil || len(form.File["file"]) == 0 {
		http.Error(w, "no files provided", http.StatusBadRequest)
		return
	}

	for _, fh := range form.File["file"] {
		err := s.processFile(dir, key, fh)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
	}

	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func (s *Server) handleDownload(w http.ResponseWriter, r *http.Request) {
	dir, key, err := s.getOrCreateSession(w, r)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	fileName := r.PathValue("file")
	fmt.Println(fileName)
	filePath := path.Join(dir, fileName)
	fmt.Println(filePath)

	// Check if the file exists
	if _, err := os.Stat(filePath); err == nil {
		in, err := os.Open(filePath)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		defer in.Close()

		err = xorCopy(w, in, key)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
	} else if errors.Is(err, os.ErrNotExist) {
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	} else {
		// Handle other potential errors, like permissions
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}

func (s *Server) handleLogo(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "logo.png")
}

func (s *Server) processFile(dir string, key []byte, fh *multipart.FileHeader) error {
	in, err := fh.Open()
	if err != nil {
		return fmt.Errorf("open: %w", err)
	}
	defer in.Close()

	safeName := sanitizeFilename(fh.Filename)
	if safeName == "" {
		return errors.New("invalid filename")
	}

	if err := os.MkdirAll(dir, 0o700); err != nil {
		return fmt.Errorf("mkdir: %w", err)
	}

	outPath := filepath.Join(dir, safeName)
	out, err := os.OpenFile(outPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o600)
	if err != nil {
		return fmt.Errorf("create: %w", err)
	}
	defer out.Close()

	err = xorCopy(out, in, key)
	if err != nil {
		return fmt.Errorf("xor copy: %w", err)
	}

	return nil
}

func xorCopy(dst io.Writer, src io.Reader, key []byte) error {
	if len(key) == 0 {
		return errors.New("empty key")
	}
	const bufSize = 64 * 1024
	buf := make([]byte, bufSize)
	out := make([]byte, bufSize)
	var pos int64

	for {
		n, rerr := src.Read(buf)
		if n > 0 {
			for i := range n {
				out[i] = buf[i] ^ key[(int(pos)+i)%len(key)]
			}
			wN, werr := dst.Write(out[:n])
			pos += int64(wN)
			if werr != nil {
				return werr
			}
			if wN != n {
				return io.ErrShortWrite
			}
		}
		if rerr != nil {
			if errors.Is(rerr, io.EOF) {
				break
			}
			return rerr
		}
	}
	return nil
}

var sidRe = regexp.MustCompile(`^[a-f0-9]{48}$`)

func (s *Server) getOrCreateSession(w http.ResponseWriter, r *http.Request) (string, []byte, error) {
	if c, err := r.Cookie(cookieName); err == nil && sidRe.MatchString(c.Value) {
		dir, key, err := s.ensureSession(c.Value)
		return dir, key, err
	}

	sid, err := newSessionID()
	if err != nil {
		return "", nil, err
	}
	dir, key, err := s.ensureSession(sid)
	if err != nil {
		return "", nil, err
	}

	ck := &http.Cookie{
		Name:     cookieName,
		Value:    sid,
		Path:     "/",
		HttpOnly: true,
		SameSite: http.SameSiteLaxMode,
		Secure:   r.TLS != nil,
		MaxAge:   int((7 * 24 * time.Hour).Seconds()),
	}
	http.SetCookie(w, ck)
	return dir, key, nil
}

func (s *Server) ensureSession(sessionID string) (string, []byte, error) {
	var err error
	var dir string
	var key []byte

	row := s.db.QueryRow(`SELECT dir, key
		FROM sessions
		WHERE session_id = ?`, sessionID)
	err = row.Scan(&dir, &key)
	if err == nil {
		return dir, key, nil
	}

	// create new session
	dir, err = os.MkdirTemp("", "storage_")
	if err != nil {
		return "", nil, err
	}

	key = make([]byte, keySize)
	if _, err := rand.Read(key); err != nil {
		return "", nil, err
	}

	_, err = s.db.Exec(`INSERT INTO sessions (session_id, dir, key)
		VALUES (?, ?, ?)`,
		sessionID, dir, key)
	if err != nil {
		return "", nil, err
	}
	return dir, key, nil
}

func newSessionID() (string, error) {
	b := make([]byte, 24) // 192 bits
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return hex.EncodeToString(b), nil
}

func sanitizeFilename(name string) string {
	base := filepath.Base(name)
	base = strings.ReplaceAll(base, string(os.PathSeparator), "_")
	base = strings.TrimSpace(base)
	if base == "." || base == ".." {
		return ""
	}
	if len(base) > 200 {
		ext := filepath.Ext(base)
		base = base[:200-len(ext)] + ext
	}
	return base
}
