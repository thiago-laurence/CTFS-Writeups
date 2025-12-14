import requests
import re
import binascii

# CONFIGURACIÓN
# Usamos un RPC público estable. Si falla, intenta con: 'https://1rpc.io/sepolia'
RPC_URL = "https://ethereum-sepolia-rpc.publicnode.com"
TX_HASH = "0x1c1e14180c2e5dceefc260208199e23a8c61524dd54bd2e378cee00e14555c14"

def solve():
    print(f"[*] Conectando a Sepolia RPC...")
    
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [TX_HASH],
        "id": 1
    }

    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        data = response.json()

        if 'result' not in data or data['result'] is None:
            print("[-] Error: Transacción no encontrada. El nodo RPC podría estar desincronizado.")
            print("[-] Intenta cambiar la URL del RPC en el script.")
            return

        # 1. Obtenemos el Input Data crudo
        raw_input = data['result']['input']
        print(f"[*] Raw Input (Hex): {raw_input[:40]}... (Total: {len(raw_input)} chars)")

        # 2. Limpieza: Quitamos '0x'
        if raw_input.startswith("0x"):
            hex_data = raw_input[2:]
        else:
            hex_data = raw_input

        # 3. Decodificación "Sucia" (Ignorando errores)
        # Convertimos hex a bytes
        try:
            byte_data = bytes.fromhex(hex_data)
        except ValueError:
            # A veces la longitud es impar, arreglamos eso añadiendo un 0 al inicio
            hex_data = '0' + hex_data
            byte_data = bytes.fromhex(hex_data)

        # Decodificamos a texto, reemplazando caracteres ilegibles con '?'
        decoded_text = byte_data.decode('utf-8', errors='replace')
        
        # Eliminamos caracteres nulos (comunes en Ethereum)
        clean_text = decoded_text.replace('\x00', '')

        print(f"[*] Texto decodificado (parcial): {clean_text}")

        # 4. Búsqueda con Regex (La parte inteligente)
        # Buscamos el patrón exacto de la flag: nexus{...}
        match = re.search(r"nexus\{.*?\}", clean_text)
        
        print("\n" + "="*40)
        if match:
            print(f"🔥 FLAG ENCONTRADA: {match.group(0)}")
        else:
            print("[-] No se detectó el patrón 'nexus{...}' automáticamente.")
            print("[-] Revisa el texto decodificado arriba por si la flag tiene otro formato.")
        print("="*40 + "\n")

    except Exception as e:
        print(f"[-] Error crítico: {e}")

if __name__ == "__main__":
    solve()