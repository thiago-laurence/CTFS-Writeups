#!/usr/bin/env python3
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from sage.all import Matrix, ZZ

# Cargar datos
with open("data.json") as f:
    data = json.load(f)

p         = int(data["p"])
factors   = [int(f) for f in data["factors"]]
hash_val  = int(data["hash"])
enc_flag  = bytes.fromhex(data["enc_flag"])
n         = len(factors)

# ─── Construcción de la Retícula Centrada ─────────────────────────────────────
# En lugar de buscar x_i en [0, 255], buscamos y_i en [-128, 127]
# donde x_i = y_i + 128.
# La ecuación queda: sum(factors[i] * (y_i + 128)) = hash (mod p)
# sum(factors[i] * y_i) = hash - sum(factors[i] * 128) (mod p)

# Calculamos el nuevo target desplazado
offset = sum(128 * f for f in factors)
target_hash = (hash_val - offset) % p

# Escalado para que LLL priorice la columna de la ecuación modular
scale = 2**150 

# Matriz (n+2) x (n+2)
# Las primeras n columnas son la identidad (pesan 1)
# La columna n es para identificar la fila del target
# La columna n+1 es la relación modular (pesa 'scale')
M = Matrix(ZZ, n + 2, n + 2)

for i in range(n):
    M[i, i] = 1
    M[i, n + 1] = factors[i] * scale

M[n, n + 1] = p * scale

# Fila del Target
M[n + 1, n] = 1  # Indicador
M[n + 1, n + 1] = -target_hash * scale

print("[*] Construyendo retícula centrada 18x18...")
print("[*] Ejecutando LLL (esto debería ser instantáneo)...")

L = M.LLL()

preimage = None
for row in L:
    # El vector solución debe tener 1 o -1 en la columna indicadora
    if abs(row[n]) == 1:
        sign = int(row[n])
        # Reconstruimos x_i = (y_i * sign) + 128
        xs = [(int(row[i]) * sign) + 128 for i in range(n)]
        
        # Validar que sean bytes y que el hash cierre
        if all(0 <= x <= 255 for x in xs):
            if sum(f * x for f, x in zip(factors, xs)) % p == hash_val:
                print(f"[+] ¡Preimage encontrada!: {xs}")
                preimage = bytes(xs)
                break

if preimage is None:
    print("[!] LLL falló. Intentando con BKZ (block_size=25)...")
    L2 = M.BKZ(block_size=25)
    for row in L2:
        if abs(row[n]) == 1:
            sign = int(row[n])
            xs = [(int(row[i]) * sign) + 128 for i in range(n)]
            if all(0 <= x <= 255 for x in xs):
                if sum(f * x for f, x in zip(factors, xs)) % p == hash_val:
                    print(f"[+] ¡Preimage encontrada con BKZ!: {xs}")
                    preimage = bytes(xs)
                    break

if preimage:
    # ─── Verificación y Descifrado ─────────────────────────────────────────────
    print(f"[*] Hash verificado: {sum(f * x for f, x in zip(factors, preimage)) % p == hash_val}")
    
    cipher = AES.new(preimage, AES.MODE_ECB)
    try:
        decrypted = cipher.decrypt(enc_flag)
        # Intentamos quitar el padding, si falla mostramos el raw
        try:
            flag = unpad(decrypted, 16).decode()
        except:
            flag = decrypted.decode(errors="replace")
        print(f"\n[+] FLAG: {flag}")
    except Exception as e:
        print(f"[!] Error al descifrar: {e}")
else:
    print("[!] No se pudo encontrar la preimagen. Revisá si data.json es correcto.")