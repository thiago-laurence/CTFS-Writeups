#!/usr/bin/env python3
"""
RSA Low Exponent Attack Script for MIND THE GAP Challenge
Solves RSA encryption when e=3 and the message is short enough that m^e < N
"""

def integer_nth_root(n, k):
    """Devuelve (root, exact) donde root = floor(n**(1/k)) y exact=True si root**k == n."""
    if n < 2:
        return n, True
    high = 1 << ((n.bit_length() + k - 1) // k)
    low = 0
    while low <= high:
        mid = (low + high) // 2
        mid_k = mid ** k
        if mid_k == n:
            return mid, True
        elif mid_k < n:
            low = mid + 1
        else:
            high = mid - 1
    return high, False

def main():
    # Challenge values from challenge.json
    N = 14508309593146392036852186367486607754388239123770045829691243154184222998048687640251024592386635569441697046704926723488988355327326504615470145691018948327744499406122769019271226177020244314074490750904060591894303295727249862117568649114289768761885684370964884412426733979181999870253163142239463480329828176240372814784781649967949154525845673601892717561048122900031676770493961212911406501893741411348182441940092726196645991558760193347770520388625214322511344330370596664171127419549482767572865387681019052778209128714326125730339472096608481806721227870805240691046645666979003932603432396724282042435777
    e = 3
    c = 5046000458278559117779134957838044135098690309585755353058261138276193482137505781482132564608553106896440785493291347385933317040883078691311015088213452902618633863936122902317586074609303885727206126845881797705002735528996492104140693057150294744361533364414645613312759904419925520873230926724120921268840005047605100307811214696752571329125
    prefix = b"openECSC{mind_the_gap_"

    print(f"N = {N}")
    print(f"e = {e}")
    print(f"c = {c}")
    print(f"prefix = {prefix.decode()}")
    print()

    # Try to compute the integer cube root of c
    root, exact = integer_nth_root(c, e)
    
    if not exact:
        print("La raíz no es exacta: c no es un cubo perfecto -> habría que usar otro método")
        return
    
    print(f"Cube root found: {root}")
    print(f"Verification: {root}^3 = {root**3}")
    print(f"Original c = {c}")
    print(f"Match: {root**3 == c}")
    print()
    
    # Convert to bytes (big-endian)
    byte_len = (root.bit_length() + 7) // 8
    pt = root.to_bytes(byte_len, "big")
    print(f"plaintext (bytes): {pt}")
    
    try:
        txt = pt.decode('utf-8')
        print(f"decoded: {txt}")
        
        if txt and txt.startswith(prefix.decode()):
            print(f"FLAG: {txt}")
        else:
            print("El texto no comienza con el prefijo esperado.")
    except Exception as ex:
        print(f"Error decoding: {ex}")

if __name__ == "__main__":
    main()