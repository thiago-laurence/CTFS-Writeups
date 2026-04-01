#!/usr/bin/env python3
"""
DinoVault exploit con SSL.
Uso: python3 exploit_ssl.py <host> <port>
"""

import ssl
import socket
import math
import sys
from Crypto.Util.number import long_to_bytes


def recv_until(sock, marker=b"\n"):
    buf = b""
    while not buf.endswith(marker):
        chunk = sock.recv(1)
        if not chunk:
            break
        buf += chunk
    return buf.decode("utf-8", errors="replace").strip()


def send(sock, data):
    sock.sendall((data + "\n").encode())


def drain_until_choice(sock):
    """Lee hasta ver el menú de opciones."""
    while True:
        line = recv_until(sock)
        if "4. Exit" in line or "What do you want" in line:
            return


def download_vexillum(sock):
    send(sock, "3")
    recv_until(sock)  # "Which encrypted dinosaur-DNA..."
    send(sock, "Vexillum Rex")
    recv_until(sock)  # "Here is the encrypted DNA..."
    enc_hex = recv_until(sock)
    recv_until(sock)  # "Use your vault key..."
    n_str = recv_until(sock)
    return enc_hex, int(n_str)


def dna_to_text(dna: str) -> str:
    lookup = {"A": 0, "T": 1, "G": 2, "C": 3}
    result = bytearray()
    for i in range(0, len(dna), 4):
        val = sum(lookup[dna[i + j]] << (j * 2) for j in range(4))
        result.append(val)
    return result.decode("utf-8", errors="replace")


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 443

    print(f"[*] Conectando a {host}:{port} (SSL)...")

    ctx = ssl.create_default_context()
    raw_sock = socket.create_connection((host, port))
    sock = ctx.wrap_socket(raw_sock, server_hostname=host)

    print("[*] Conexión SSL establecida.")

    drain_until_choice(sock)

    print("[*] Descarga 1 de Vexillum Rex...")
    enc1, n1 = download_vexillum(sock)
    print(f"    n1 = {str(n1)[:50]}...")

    recv_until(sock)  # "What do you want to do now?"

    print("[*] Descarga 2 de Vexillum Rex...")
    enc2, n2 = download_vexillum(sock)
    print(f"    n2 = {str(n2)[:50]}...")

    sock.close()

    print("[*] Calculando GCD...")
    q = math.gcd(n1, n2)

    if q in (1, n1, n2):
        print(f"[!] GCD inválido. Intentá de nuevo.")
        return

    print(f"[+] Factor encontrado!")
    p = n1 // q
    phi = (p - 1) * (q - 1)
    e = 2**16 + 1
    d = pow(e, -1, phi)

    c = int(enc1, 16)
    m = pow(c, d, n1)

    dna = long_to_bytes(m).decode("ascii", errors="replace")
    plaintext = dna_to_text(dna)

    print(f"\n[+] FLAG: {plaintext}")


if __name__ == "__main__":
    main()