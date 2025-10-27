#!/usr/bin/env python3
import socket

HOST = "challenge.secso.cc"
PORT = 7002
pwd = "36313634366436393665"

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
    return data

with socket.create_connection((HOST, PORT), timeout=5) as s:
    # recibir banner / menú inicial
    print(recv_all(s).decode(errors="ignore"))

    # elegir opción 2 (Login)
    s.sendall(b"2\n")
    print(recv_all(s).decode(errors="ignore"))

    # enviar login
    s.sendall(b"admin\n")
    # enviar password
    s.sendall((pwd + "\n").encode())
    # leer respuesta final (flag)
    out = recv_all(s, timeout=2.0).decode(errors="ignore")
    print("=== OUTPUT ===")
    print(out)
