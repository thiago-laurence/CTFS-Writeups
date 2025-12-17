# Pyjail

**Flag encontrada:** `infobahn{Y0u_3Sc4p3D_Th3_J@1lll_4359849084894}`

## 1) Resúmen rápido

El reto ofrece un *jail* que ejecuta código Python recibido por entrada y captura `stdout`. Restricciones clave:

- Entrada ≤ 15 caracteres.
- Solo caracteres permitidos: `a–z` y espacio.
- El entorno ejecuta `exec(code, {})` y captura la salida con `contextlib.redirect_stdout`.
- Si la salida tiene más de 500 caracteres, el programa revela la flag.

El bypass consiste en importar un módulo que, al importarse, **escribe texto largo en stdout** sin necesidad de paréntesis, comillas, ni caracteres prohibidos. El módulo estándar que cumple esto es `this` (el “Zen of Python”). El payload exitoso es:

```
import this
```

Para enviar el payload al servicio se usó la conexión que daba el reto por TCP:

```
nc pyjail.challs.infobahnc.tf 1337
```

---

## 2) Metodología (pasos)

### 2.1 Entender el vector

- `exec(code, {})` ejecuta código como script — no hay impresión automática del valor de la última expresión (a diferencia del REPL).
- No se permiten paréntesis ni comillas, por lo que `print(...)` o `open('flag.txt')` están descartados.
- Necesitamos que el código **escriba en stdout** durante su ejecución y que esa salida sea lo suficientemente larga (>500).

### 2.2 Buscar módulos con efectos en `import`

- Algunos módulos ejecutan código en su cuerpo en el momento del `import` (p. ej. prints automáticos).
- `this` es el candidato clásico: al importarlo escribe la “Zen of Python” en stdout.

### 2.3 Construir payload dentro de las restricciones

- `import this` usa sólo letras y un espacio (cumple el conjunto permitido) y tiene longitud ≤ 15.
- Al ejecutarlo bajo `exec` produce salida capturada por `redirect_stdout`.

### 2.4 Envío al servicio

- Abrir una conexión netcat al host y puerto proporcionados:
    
    ```
    nc pyjail.challs.infobahnc.tf 1337
    ```
    
- Pegamos `import this` y enviar. El jail ejecuta, captura la salida y, al superar 500 caracteres, imprime la flag.

---

## 3) Payload (exacto a enviar)

```
import this
```

— 11 caracteres, sólo letras y un espacio, cumple todas las restricciones.

---

## 4) Ejecución y verificación

- Conexión:
    
    ```
    nc pyjail.challs.infobahnc.tf 1337
    ```
    
- En la prompt que devuelve el reto, introducir:
    
    ```
    import this
    ```
    
- Resultado observado (ejemplo desde el reto):
    
    ```
    b'infobahn{Y0u_3Sc4p3D_Th3_J@1lll_4359849084894}\n'
    ```
    
    → flag recuperada.
    

Si querés probar localmente el comportamiento antes de atacar el servicio, recreá la función `run` que usa el reto y verificá:

```python
import io, contextlib

def run(code):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {})
    except Exception:
        return None
    return buf.getvalue() or None

r = run("import this")
print(len(r))   # debería ser > 500 en Python estándar
print(r[:200])  # inspeccionar comienzo de la salida
```

---

## 6) Lecciones y buenas prácticas (para autores de retos / admins)

- **No ejecutar `exec` directamente con entrada del usuario** sin restricciones fuertes.
- **Deshabilitar imports** si no son necesarios: por ejemplo, evaluar el AST y bloquear nodos `Import` / `ImportFrom`.
- Ejecutar código dentro de un sandbox real (contenedor limitado, sin módulos estándar accesibles) o con `__builtins__` restringido:
    
    ```python
    exec(code, {"__builtins__": {}})
    ```
    
    (con cuidado: algunas funciones internas aún pueden estar expuestas por otras vías).
    
- No basar decisiones de seguridad en la cantidad de `stdout`. `stdout` puede ser controlado por módulos estándar o por módulos instalados.
- Limitar módulos disponibles y realizar análisis estático (AST) para filtrar patrones peligrosos.