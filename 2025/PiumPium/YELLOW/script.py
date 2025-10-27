#!/usr/bin/env python3
import struct
from pathlib import Path
import re

def extract_flag_from_png(file_path):
    data = Path(file_path).read_bytes()
    i = 8  # saltar cabecera PNG
    idat_lengths = []
    while i < len(data):
        if i + 8 > len(data):
            break
        length = struct.unpack(">I", data[i:i+4])[0]
        ctype = data[i+4:i+8].decode('latin1', errors='ignore')
        if ctype == "IDAT":
            idat_lengths.append(length)
        i = i + 12 + length  # avanzar al siguiente chunk
    chars = [chr(l) for l in idat_lengths if 32 <= l <= 126]
    decoded = ''.join(chars)
    match = re.search(r"openECSC\\{.*?\\}", decoded)
    return match.group(0) if match else decoded

if __name__ == "__main__":
    file = "yellow.png"
    flag = extract_flag_from_png(file)
    print("Flag encontrada:", flag)