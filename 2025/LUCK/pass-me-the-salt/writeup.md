# DSA-LUCK CTF Write-up - Pass Me the Salt


## Descripción del Desafío

El desafío nos presenta un servicio que maneja cuentas de usuario con un sistema de login. El servidor nos proporciona el código fuente en Python para que podamos analizarlo y encontrar la vulnerabilidad.
<img width="590" height="608" alt="image" src="https://github.com/user-attachments/assets/568a78cb-8da4-4c42-aae1-3b1767311b82" />


## Análisis del Código

Al revisar el código Python se encontró una inconsistencia crítica entre dos funciones:

### Función de Creación de Cuenta
```python
def create_account(login, pwd):
    # Calcula hash con: sha1(salt + (pwd).encode())
```

### Función de Login  
```python
def check_login(login, pwd):
    # Calcula hash con: salt + bytes.fromhex(pwd)
```

### El Problema
La cuenta de admin se crea de esta manera:
```python
create_account("admin", "admin".encode().hex())
```

Esto significa que:
1. `"admin".encode().hex()` produce la string `"61646d696e"`
2. La función `create_account` convierte esto a bytes con `.encode()`
3. Se almacena el hash de: `salt + b"61646d696e"` (los bytes literales de los caracteres 6,1,6,4,6,d,6,9,6,e)

**Pero en el login**, la función `check_login` usa `bytes.fromhex(pwd)`, que interpreta la entrada como hexadecimal.

## La Vulnerabilidad

La inconsistencia está en que:
- **Al crear la cuenta**: se almacena el hash de los caracteres literales "61646d696e"
- **Al hacer login**: se interpreta la entrada como hexadecimal

Para explotar esto, necesito encontrar una entrada X tal que:
```
bytes.fromhex(X) == b"61646d696e"
```

## Solución

Necesitamos convertir cada carácter de la string "61646d696e" a su valor hexadecimal ASCII:

- '6' → 0x36 → 36
- '1' → 0x31 → 31  
- '6' → 0x36 → 36
- '4' → 0x34 → 34
- '6' → 0x36 → 36
- 'd' → 0x64 → 64
- '6' → 0x36 → 36
- '9' → 0x39 → 39
- '6' → 0x36 → 36
- 'e' → 0x65 → 65

Concatenando todos estos valores: `36313634366436393665`

## Explotación Manual

1. Conectarse al servicio: `nc challenge.secso.cc 7002`
2. Elegir la opción "2" (Login)
3. Introducir:
   - **Login**: `admin`
   - **Password**: `36313634366436393665`

El servidor interpretará la password como hexadecimal, lo convertirá a `b"61646d696e"`, calculará el hash y coincidirá con el almacenado.

## Script de Explotación


```python
#!/usr/bin/env python3
# exploit.py

import socket
import time

HOST = "challenge.secso.cc"
PORT = 7002
LOGIN = "admin"
PASSWORD_HEX = "36313634366436393665"  # payload de explotación

def recv_all(sock, timeout=1.0):
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            part = sock.recv(4096)
            if not part:
                break
            data += part
    except Exception:
        pass
    return data.decode(errors="ignore")

def main():
    print(f"[+] Conectando a {HOST}:{PORT} ...")
    with socket.create_connection((HOST, PORT), timeout=10) as s:
        # Leer banner inicial
        banner = recv_all(s, timeout=1.5)
        print(banner, end="")

        # Elegir Login (opción 2)
        s.sendall(b"2\n")
        time.sleep(0.05)
        print(recv_all(s, timeout=0.8), end="")

        # Enviar credenciales de explotación
        s.sendall((LOGIN + "\n").encode())
        time.sleep(0.05)
        s.sendall((PASSWORD_HEX + "\n").encode())

        # Recibir respuesta con la flag
        output = recv_all(s, timeout=2.0)
        print("\n=== RESPUESTA DEL SERVIDOR ===\n")
        print(output)

if __name__ == "__main__":
    main()
```

## Ejecución

**Uso del script:**
```bash
python3 exploit.py
```

## Flag
La flag se obtiene al hacer login exitoso con las credenciales explotadas.
Flag: K17CTF{s4Lt_4nD_p3pper_is_ov3rr4t3d}

