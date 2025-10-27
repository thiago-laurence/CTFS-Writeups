#!/usr/bin/env python3
import struct
from pathlib import Path

# try to locate the image relative to this script: resources/yellow/yellow.png
base = Path(__file__).parent
paths = [base / "resources" / "yellow" / "yellow.png", base / "resources" / "yellow.png", base / "yellow.png"]
for p in paths:
    if p.exists():
        data = p.read_bytes()
        break
else:
    raise FileNotFoundError(f"Could not find yellow.png in any of: {paths}")

# simple parser: recorre chunks a partir del byte 8 (después de la firma PNG)
i = 8
idat_lengths = []
while i < len(data):
    if i + 8 > len(data):
        break
    length = struct.unpack(">I", data[i:i+4])[0]
    ctype = data[i+4:i+8].decode('latin1', errors='ignore')
    if ctype == "IDAT":
        idat_lengths.append(length)
    i = i + 12 + length  # length(4) + type(4) + data(length) + crc(4)

# convertir longitudes a caracteres ASCII cuando sea imprimible
chars = []
for l in idat_lengths:
    if 32 <= l <= 126:
        chars.append(chr(l))
    else:
        # si hay un valor no imprimible, lo representamos como punto
        chars.append('.')

decoded = ''.join(chars)
print("Decoded from IDAT lengths:")
print(decoded)
# si la flag está en el texto, mostrarla explícitamente (busca {...})
import re
m = re.search(r"\{.*?\}", decoded)
if m:
    print("\nFlag encontrada:", decoded[m.start()-len("openECSC"):m.end()])  # intenta mostrar whole token
else:
    # fallback: mostrar el decoded completo
    print("\nPosible flag/cadena:", decoded)