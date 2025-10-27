# Writeup: openECSC CTF - "Surely I can just swap e and d, right?" (Crypto 100 pts)

## Challenge Overview

Este reto nos presenta un escenario de RSA donde el creador decidió, de manera muy poco convencional, intercambiar los exponentes público y privado:

* Genera dos primos grandes p y q de 1024 bits cada uno.
* Calcula N = p * q y selecciona un pequeño e de 500 bits.
* Calcula d = e^{-1} mod phi(N).
* **Finalmente intercambia e y d**.

Además, nos dan:

* primes: 9 primos pequeños de 256 bits.
* e_residues: los residuos e % prime para cada primo de primes.
* ct: el flag cifrado con AES-ECB usando la clave sha256(str(p) + str(q)).

El objetivo es recuperar la flag.

## Vulnerabilidad clave

El swap e, d = d, e deja **un d privado extremadamente pequeño** (~500 bits), lo que rompe la seguridad de RSA clásica y permite usar *el ataque de Wiener*, que recupera exponentes privados pequeños cuando d < N^{0.25}.

Además, el reto nos da residuos de e módulo primos pequeños, lo que permite reconstruir el exponente completo mediante *CRT (Chinese Remainder Theorem)*.

## Paso 1: Reconstruir e con CRT

Dado que:


e_residues[i] = e % primes[i]


podemos usar el Teorema Chino del Resto para obtener el valor de e:

python
def crt(remainders, moduli):
    M = 1
    for m in moduli: M *= m
    x = 0
    for r, m in zip(remainders, moduli):
        Mi = M // m
        inv = pow(Mi, -1, m)
        x += r * Mi * inv
    return x % M

reconstructed_e = crt(e_residues, primes)


Esto nos da el e exacto usado en el reto, suficiente para intentar atacar RSA.

## Paso 2: Ataque de Wiener

Wiener nos dice que si d es suficientemente pequeño, podemos encontrarlo a partir de los **convergentes de la fracción continua de e/N**.

* Construimos la fracción continua de e/N.
* Calculamos todos los convergentes (k, d).
* Para cada convergente válido, probamos si d es el exponente privado resolviendo:


phi = (e*d - 1)//k
s = N - phi + 1


* Factorizamos N resolviendo x^2 - s x + N = 0.

Si encontramos p y q que multiplican N, hemos recuperado la clave privada d y los primos originales.

## Paso 3: Recuperar la clave AES

Una vez obtenidos p y q, la clave AES se genera como:

python
from hashlib import sha256
key = sha256((str(p) + str(q)).encode()).digest()


El flag está cifrado en AES-ECB con padding PKCS7, así que basta con descifrarlo:

python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
cipher = AES.new(key, AES.MODE_ECB)
flag = unpad(cipher.decrypt(ct), 16)
print(flag.decode())


## Paso 4: La Flag

Ejecutando todos los pasos anteriores, se obtiene la flag:


openECSC{0h_n0!M4yb3_I_sh0uldn'7_sw4p_e_4nd_d_4f73r_4ll...}


## Conclusión / Lecciones

1. **Nunca intercambiar e y d**: deja la clave privada pequeña y vulnerable.
2. **Exponer residuos o partes de e** puede permitir reconstrucciones completas usando CRT.
3. Ataques clásicos de criptografía (Wiener) siguen siendo relevantes si se cometen errores en la elección de parámetros.

Este reto es un ejemplo perfecto de cómo una mala decisión de implementación puede romper toda la seguridad de RSA, incluso cuando los números parecen grandes y seguros.

---

Fin del writeup.