# syntax=docker/dockerfile:1
FROM golang:1.24-trixie
WORKDIR /app

COPY challenge/go.mod challenge/go.sum challenge/main.go challenge/logo.png ./
RUN echo "nexus{fake_flag}" > /flag.txt

RUN go mod download

RUN CGO_ENABLED=1 GOOS=linux go build -o main

RUN chmod 0644 /flag.txt

RUN useradd -m ctf
RUN chown -R ctf:ctf /app
USER ctf

EXPOSE 8080

CMD ["/app/main"]
