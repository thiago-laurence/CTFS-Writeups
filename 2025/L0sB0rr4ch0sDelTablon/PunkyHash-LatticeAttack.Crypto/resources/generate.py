#!/usr/bin/env python3

import json
import random

from Crypto.Cipher import AES
from Crypto.Util.number import getPrime
from Crypto.Util.Padding import pad

FLAG = "dach2026{xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx}"

pbits = 137
p = getPrime(pbits)
key_bits = 16

# Generate hash of the key
factors = [random.SystemRandom().randint(0, p-1) for _ in range(key_bits)]
preimage = [random.SystemRandom().randint(0, 0xff) for _ in range(key_bits)]
hash = sum([factors[i] * preimage[i] % p for i in range(key_bits)]) % p

# Encrypt flag
key = bytes(preimage)
cipher = AES.new(key, AES.MODE_ECB)
enc = cipher.encrypt(pad(FLAG.encode(), 16)).hex()

data = {
    "p": p,
    "factors": factors,
    "hash": hash,
    "enc_flag": enc
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=4)
