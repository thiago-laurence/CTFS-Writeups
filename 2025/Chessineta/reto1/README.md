# 🔐 Challenge: Secure Storage

**Categoría:** Web 

## 📝 Análisis del Mecanismo
Tras revisar el código fuente (Golang) y el entorno Docker, se detectó que el servidor no procesaba las rutas de archivos en texto plano. Implementaba una capa de "seguridad" por oscuridad antes de acceder al sistema de archivos.

El mecanismo era una operación **XOR (Exclusive OR)**. El servidor combinaba la entrada del usuario con una clave (Key) estática.

**Lógica del Servidor:**
```math
Ruta_Final = Input_Usuario \oplus Clave_XOR
```

## 🧠 Vector de Ataque

### 1. El Problema del Path Traversal
El objetivo era realizar un Path Traversal clásico (`../../../flag.txt`). Sin embargo, al enviar esta cadena en texto plano, el servidor la "desencriptaba" (aplicando XOR), resultando en bytes basura que no correspondían a ninguna ruta válida.

### 2. Known Plaintext Attack (Recuperación de la Clave)
Para poder enviar un payload válido, necesitábamos conocer la **Clave XOR**. Utilizamos un ataque de texto plano conocido:
1.  **Plaintext:** Descargamos el archivo `/logo.png` de forma legítima (público).
2.  **Ciphertext:** Descargamos el mismo archivo a través del endpoint vulnerable (`/download/...`).
3.  **Cálculo:** Debido a las propiedades conmutativas de XOR, pudimos recuperar la clave:

```math
Clave = Plaintext \oplus Ciphertext
```

## 🧨 Explotación

Se desarrolló un script automatizado en Python que realiza los siguientes pasos:
1.  Sube un archivo temporal para obtener una sesión válida.
2.  Descarga el recurso público y su versión cifrada para calcular la **Keystream**.
3.  Descarga la flag cifrada mediante Path Traversal.
4.  Descifra la flag localmente usando la clave recuperada.

### 💻 Ejecución
El exploit completo se encuentra en el archivo adjunto [`exploit.py`](./exploit.py).

```bash
python3 exploit.py
```

**Salida del script:**
```text
[+] Iniciando ataque contra [http://ctf.nexus-security.club:6213](http://ctf.nexus-security.club:6213)
[*] Descargando logo original (/logo.png)...
[*] Descargando logo cifrado usando traversal...
[+] Clave recuperada (hex): a1b2c3...
[*] Descargando flag cifrada...
========================================
FLAG DESCIFRADA: nexus{l34k_7h3_k3y_br34k_7h3_c1ph3r}
========================================
```

## 🚩 Flag
> `nexus{l34k_7h3_k3y_br34k_7h3_c1ph3r}`

