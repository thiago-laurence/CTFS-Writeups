#!/usr/bin/env python3
import sys

# cargar diccionario
with open("emoji.txt", "r", encoding="utf-8") as f:
    emoji = list(f.read().strip())

decode_table = {ch: i for i, ch in enumerate(emoji)}

def decode(enc):
    # sacar el padding 🚀
    enc = enc.rstrip("🚀")
    bits = ""
    for ch in enc:
        val = decode_table[ch]
        bits += f"{val:010b}"   # extraer 10 bits
    # agrupar en bytes
    out = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        out.append(int(byte, 2))
    return out

if __name__ == "__main__":
    #flag_enc = "🪛🔱🛜🫗🚞👞🍁🎩🚎🐒🌬🧨🖱🥚🫁🧶🪛🔱👀🔧🚞👛😄🎩🚊🌡🌬🧮🤮🥚🫐🛞🪛🔱👽🔧🚞🐻🔳🎩😥🪨🌬🩰🖖🥚🫐🪐🪛🔱👿🫗🚞🏵📚🎩🚊🎄🌬🧯🕺🥚🫁📑🪛🔰🐀🫗🚞💿🔳🎩🚲🚟🌬🧲🚯🥚🫁🚰🪛🔱💀🔧🚞🏓🛼🎩🚿🪻🌬🧪🙊🥚🫐🧢🪛🔱🛟🔧🚞🚋🫳🎩😆🏉🌬🧶🚓🥚🫅💛🪛🔱🔌🐃🚞🐋🥍🎩😱🤮🌬🩰🛳🥚🫀📍🪛🔰🐽🫗🚞💿🍁🎩🚊🌋🌬🧵🔷🚀🚀🚀"
    second_flag = "🪛🔰🛏🍈📛🤵🔈🚁📷🦨🥩💇💼🥇🧷🥳🎆🚇🔅👶📷🚇🤧🗣💐🥵🌚🦽🏖🧇🪥🦿🏋🛜🙆🧀🏋🔭🥬🍲🔫🚀🚀🚀"
    test = "🐴🙅🥬🍴🎉🚀🚀🚀"
    decoded = decode(second_flag)
    print("Bytes decodificados:", decoded)
    try:
        print("Texto decodificado:", decoded.decode())
    except:
        print("No se puede decodificar directamente como UTF-8, revisar codificación adicional.")
