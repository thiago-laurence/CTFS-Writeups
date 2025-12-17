# Linearity

**Flag encontrada:** `infobahn{You_HAVE_Aff1niTy_f0rCrypto}`

## 1) Resumen rápido

El reto genera una lista **C** usando una matriz **M** construida a partir de un vector **V** y factores aleatorios, y luego hace XOR con los bytes del FLAG:

[C[i] = M[(i // 5) % 5][i % 5] \oplus \text{ord}(\text{FLAG}[i]) ]

**Objetivo:** recuperar **FLAG** conociendo **V** y **C**. Se resolvió sin brute-force completo aprovechando la **linealidad por columnas**.

### 1.2  Reto Completo:

```python
from random import randint
from hashlib import sha256
from secret import FLAG

V = [randint(0, 100) for i in range(5)]
M = [[V[i] * randint(0, 100) for i in range(5)] for i in range(5)]
C = [M[i // 5 % 5][i % 5] ^ ord(FLAG[i]) for i in range(len(FLAG))]

print(f"{V = }")
print(f"{C = }")
print(sha256(FLAG.encode()).digest().hex())

# Flag output:
# V = [14, 38, 56, 76, 51]
# C = [1357, 2854, 1102, 1723, 4416, 283, 344, 4566, 5023, 1798, 477, 3833, 1839, 5416, 4017, 1066, 161, 415, 5637, 1696, 1058, 3025, 5286, 5141, 3818, 1373, 2839, 1102, 1764, 4432, 313, 322, 4545, 5012, 1835, 477, 3825]
# e256693b7b7d07e11f2f83f452f04969ea327261d56406d2d657da1066cefa17
```

---

## 2) Metodología (pasos)

### 2.1 Entender el cifrado

- Índices: `row = (i//5)%5`, `col = i%5`.
- Construcción: `M[row][col] = V[col] * r` para algún entero `r ∈ [0..100]` (según el generador).

### 2.2 Prefijo/sufijo conocidos

- Prefijo supuesto/confirmado: `infobahn{` y sufijo `}`.
- Para cada `i` con carácter conocido: `M[row][col] = C[i] ^ ord(known_char)` → recupera celdas de **M**.

### 2.3 Propagación directa

- Con celdas de **M** conocidas, para toda `i` que las use: `FLAG[i] = chr(C[i] ^ M[row][col])` → revela gran parte del FLAG.

### 2.4 Candidatos acotados por posición

- Para posiciones aún desconocidas: usar `M[row][col] = V[col]*r` con `r ∈ [0..100]`.
- Para cada `r`, calcular `b = C[i] ^ (V[col]*r)` y filtrar `b` por **ASCII imprimible/alfabeto plausible**.
- Resultado: listas de candidatos por índice (tamaños pequeños).

### 2.5 Medición y decisión de búsqueda

- Producto de listas ≈ **8,128,512** combinaciones (manejable).
- Brute-force solo sobre ese espacio reducido (no sobre 256^n).

### 2.6 Brute-force eficiente (mixed‑radix + paralelo)

- Base con posiciones fijas en `bytearray`.
- Enumeración **mixed‑radix** sobre índices ambiguos (radices = tamaños de listas).
- Paralelización con `multiprocessing.Pool`.
- Comprobación rápida con `hashlib.sha256` (C) y operaciones in‑place.
- Heurísticas: priorizar candidatos plausibles (letras/números típicos).

---

## 3) Resultado

- Se probaron ~**8.13M** combinaciones en paralelo.
- **Flag encontrada:** `infobahn{You_HAVE_Aff1niTy_f0rCrypto}`.
- **Tiempo observado:** ~**0.11 s** (gracias a heurísticas + paralelización).

---

## 4) Código clave (resumen)

- **Propagación de M** desde prefijo/sufijo y generación de candidatos con `r ∈ [0..100]`.
- **Brute-force mixed‑radix paralelo:** divide el espacio por radices y reparte bloques; usa `bytearray` + `hashlib.sha256` para validar.

> Si se requiere, se pueden adjuntar snippets limpios: script de propagación y bruteforce_candidates.py.
> 

---

## 5) Lecciones y buenas prácticas

- **Explotar estructura**: cuando haya “linearity/matrices”, reconstruir estado/clave parcial (aquí, **M**) a partir de info conocida.
- **Reducir el dominio** antes de brute‑force: pasar de `256^n` a `∏ |candidatos[i]|` cambia la complejidad.
- **Brute-force optimizado**: mixed‑radix + `bytearray` + hash en C + **paralelización** es ideal para 10^6–10^8 combinaciones.
- **Heurísticas de plausibilidad** aceleran el hallazgo de flags legibles.