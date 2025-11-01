# WriteUp de resolución de retos para Trabajo final de DSA

Para realizar este trabajo, complete varios retos que no incluí acá porque no pude hacer, en el mismo CTF, todos los retos necesarios para completar el trabajo. Luego decidí dejar también los retos que no había podido completar, es por eso que se incluye en el WriteUp el CTF *Securinets*, a pesar de estar incomplete. Finalmente, los retos de *V1t* fueron más sencillos y pude completar los retos necesarios.  

## Securinets CTF

### Puzzle - Web

![alt text](images/image.png)

El reto comienza dandonos una copia del código con un Dockerfile para replicar el entorno. Dentro del código, hay muchas rutas divididas en dos bloques principales: *auth.py*, donde se encuentran las rutas relacionadas a registro, y *routes.py*, donde están el resto de las rutas. Analizando el código, vemos que hay distintos roles: usuario, editor y admin. Es lógico suponer que nuestro objetivo es loguearnos como admin. Al registrar un usuario, vemos en la ruta *confirm-register* que podemos manipular el formulario para crearnos un usuario **editor**, pero no un admin. Creamos un script para esto (Script.py) y lo ejecutamos.  
Estar logueados como editor nos permite el acceso a distintas rutas que ser usuario no nos permite. Principalmente, vemos que podemos acceder a la ruta */users/<uuid>*. En esa ruta podremos acceder a la información de cualquier usuario, ya que no hay ningún tipo de control de accceso y, sobre todo, las contraseñas están guardadas en texto plano. Por tanto, nuestro objetivo es conseguir el uuid del admin.  
Analizando el resto de las rutas de **routes.py** vemos que podemos crear artículos con colaboradores, y esto crea una entrada en la tabla *collab_requests* con los **uuid** de los participantes. Esto podemos hacerlo directamente desde la página con el nombre de nuestro colaborador, que será **admin**. Nuestro objetivo ahora será acceder a esta collab_request. Vemos que hay dos rutas que acceden a esta tabla y que potencialmente podrían servirnos: *collab/request* y *collab/requests*. Sin embargo, ambas tienen una protección para que solo pueden ser accedidas desde el propio contenedor Docker do  nde están almacenadas, y es una protección que no podemos vulnerar.  
Nos enfocamos entonces en la ruta */collab/accept/<string:request_uuid>*. Analizandola, vemos que la ruta permite aceptar una colaboración, lo que publicaría el artículo. La ruta no tiene ningún tipo de control de acceso: no chequea quién es la persona que está accediendo ni que esta persona sea la misma a la que se le solicitó la colaboración, simplemente, chequea que sea un usuario existente y que no sea admin. Para entrar a esta ruta es necesario tener el **uuid** de la request. Este es un dato que aparece "oculto" en el listado de colaboraciones.  
![alt text](images/image-1.png)  
Una vez con este dato, enviamos la request con curl

```bash
❯ curl -X POST http://<ruta>/collab/accept/<request-uuid> \
  -b "session=cookie-del-usuario-editor"
```

![alt text](images/image-4.png)  
Esto nos acepta la colaboración y publica el artículo. Podemos ver los artículos en el navegador, e inspeccionando el código podremos ver el **uuid** de los colaboradores.  ![alt text](images/image-2.png)  
Con esta información, finalmente podemos acceder a la información del administrador.  
![alt text](images/image-3.png)  

Logueado como administrador, puedo entrar al panel de admin, que me da acceso a una ruta muy sospechosa llamada *ban_users*. Después de dar muchas vueltas, veo que finalmente esa ruta no me es útil. Estando como administrador tambien tengo acceso a la ruta */data* donde encuentro dos archivos: **secrets.zip** y **db_connect.exe**. El zip tiene una contraseña que lo protege, intento forzarla con **john** y con **fcrackzip** sin exito. Me vuelco al otro archivo y lo analizo con **strings**, allí encuentro las credenciales de la base de datos, entre ellas la contraseña. Pruebo esta contraseña en el .zip y finalmente encuentro la flag.  
![alt text](images/image-5.png)  

![alt text](images/image-6.png)

### S3cret5 - Web

![alt text](images/image-7.png)
El reto comienza con un formulario de login y register. Nuevamente nos dan el código y, lo que se asume, es que tenemos que escalar a admin, ya que hay varias rutas a las que no podemos acceder, y todo está debidamente protegido. Sin embargo, existe la función */report* que, de entrada, se ve muy sospechosa.  

```js
router.post("/", authMiddleware, async (req, res) => {
  const { url } = req.body;

  if (!url || !url.startsWith("http://localhost:3000")) {
    return res.status(400).send("Invalid URL");
  }

  try {
    const admin = await User.findById(1);
    if (!admin) throw new Error("Admin not found");

    const token = jwt.sign({ id: admin.id, role: admin.role }, JWT_SECRET, { expiresIn: "1h" });

    // Launch Puppeteer
    const browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    });

    const page = await browser.newPage();

    // Set admin token cookie
    await page.setCookie({
      name: "token",
      value: token,
      domain: "localhost",
      path: "/",
    });

    // Visit the reported URL
    await page.goto(url, { waitUntil: "networkidle2" });
    const html = await page.content();

    await browser.close();

    res.status(200).send("Thanks for your report");
  } catch (error) {
    console.error(error);
    res.status(200).send("Thanks for your report");
  }
});
```

Lo que se ve acá es que, al reportar una ruta, un **pupeteer** con privilegios de admin visita esa ruta. A partir de esto, intenté enviar muchos payloads tanto a los mensajes como a los secretos para luego reportarlos e intentar que el pupeteer los ejecute como admin. Nada de esto funciono porque todas las vistas están correctamente salvadas contra XSS reflejado y almacenado.  
Lo que tenemos es qué un admin va a visitar la página que le indiquemos, pero no podemos manipularlo para que haga nada más. Excepto que, la misma página envíe algo al ser visitada. Es el caso de *profile.ejs*. En esa vista hay un script que envía un log al visitarla.

```js
fetch("/log/"+profileId, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          userId: "<%= user.id %>", 
          action: "Visited user profile with id=" + profileId,
          _csrf: csrfToken
        })
      })
      .then(res => res.json())
      .then(json => console.log("Log created:", json))
      .catch(err => console.error("Log error:", err));
```

Convenientemente, el log es un POST que envía el userId del usuario actual. Si manipulamos la variable profileId, podemos enviar un POST a otro lado con nuestro userId en el cuerpo del POST. La ruta a la que hay que enviarlo es a la de *addAdmin*, que envía un POST con un id para convertilo en admin. Sin embargo, esta ruta requiere que el usuario que la envía se admin, por eso necesitamos que la envie el pupeteer. 
Ingresando el payload *http://localhost:3000/user/profile/?id=5&id=../admin/addAdmin* forzamos al pupeteer a que vaya a nuestro perfil y a la vez manipulamos la variable para redireccionar el fetch. Con esto nos convertimos en admin.

![alt text](images/image-8.png)  
![alt text](images/image-9.png)

A partir de acá, no pude resolverlo. Mi sospecha principal y la estrategia que probé fue un ataque de SQLi sobre la función del Model me msgs *findAll*, con el fin de extraer la flag de la tabla **flags** (los *console.log* son propios para debug):

```js
findAll: async (filterField = null, keyword = null) => {
    const { clause, params } = filterHelper("msgs", filterField, keyword);

    const query = `
      SELECT msgs.id, msgs.msg, msgs.type, msgs.createdAt, users.username
      FROM msgs
      INNER JOIN users ON msgs.userId = users.id
      ${clause || ""}
      ORDER BY msgs.createdAt DESC
    `;

    console.log("[DEBUG] Query construida:", query);
    console.log("[DEBUG] Parámetros:", params);

    const res = await db.query(query, params || []);
    return res.rows;
  },
```

Esto llama al helper *filterHelper* para ayudarlo a construir la claúsula por la que filtra.

```js
function filterBy(table, filterBy, keyword, paramIndexStart = 1) {
  if (!filterBy || !keyword) {
    return { clause: "", params: [] };
  }

  const clause = ` WHERE ${table}."${filterBy}" LIKE $${paramIndexStart}`;
  const params = [`%${keyword}%`];

  return { clause, params };
}
```

Por la forma en que está construida la query, el parámetro *keyword*, que es el que nosotros podemos controlar desde el formulario de la web, está correctamente salvado y parametrizado. Pero el parámetro *filterBy* no, y es vulnerable a SQLi. Sin embargo, por la manera en que está construida la query, no logré armar el payload adecuado: las comillas entre las que está encerrado el parámetro en el String de js y la forma en que está construido el string me impedían comentar el resto de la query, por lo que no pude lograr una sentencia que incluya al LIKE y al ORDERBY siguientes con un UNION que me permitan extraer la flag. Probé muchos payloads, algunos de los cuales quedaron guardados en el script *postAMessage.py*, pero no logré dar con el adecuado.

## V1t CTF

### Login - Web

**Flag**: v1t{p4ssw0rd}

Para resolver el reto nos dan una URL donde debemos loguearnos. Cuando analizamos la página en cuestión, vemos que no tiene ningún contenido en el body salvo un **script**.  

```javascript
    async function toHex(buffer) {
      const bytes = new Uint8Array(buffer);
      let hex = '';
      for (let i = 0; i < bytes.length; i++) {
        hex += bytes[i].toString(16).padStart(2, '0');
      }
      return hex;
    }

    async function sha256Hex(str) {
      const enc = new TextEncoder();
      const data = enc.encode(str);
      const digest = await crypto.subtle.digest('SHA-256', data);
      return toHex(digest);
    }

    function timingSafeEqualHex(a, b) {
      if (a.length !== b.length) return false;
      let diff = 0;
      for (let i = 0; i < a.length; i++) {
        diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
      }
      return diff === 0;
    }

    (async () => {
      const ajnsdjkamsf = 'ba773c013e5c07e8831bdb2f1cee06f349ea1da550ef4766f5e7f7ec842d836e'; // replace
      const lanfffiewnu = '48d2a5bbcf422ccd1b69e2a82fb90bafb52384953e77e304bef856084be052b6'; // replace

      const username = prompt('Enter username:');
      const password = prompt('Enter password:');

      if (username === null || password === null) {
        alert('Missing username or password');
        return;
      }

      const uHash = await sha256Hex(username);
      const pHash = await sha256Hex(password);

      if (timingSafeEqualHex(uHash, ajnsdjkamsf) && timingSafeEqualHex(pHash, lanfffiewnu)) {
        alert(username+ '{'+password+'}');
      } else {
        alert('Invalid credentials');
      }
    })();
```

En el script, vemos que nos pide un username y una password, a eso le aplica un hash SHA256 y lo compara con las variables donde tiene guardado el hash del username y la password. Por tanto, lo que debemos hacer es buscar la palabra que, al aplicarle el hash SHA256, sea igual a los hashes ahi expuestos. Hay diferentes herramientas online que pueden hacer eso, entre ellas "hashes.com".  
Buscamos ambos hashes y obtenemos el username y la password:  
![alt text](imagesV1t/image.png)
![alt text](imagesV1t/image-1.png)  
Una vez obtenidas, nos logueamos y eso nos devuelve la flag:  
![alt text](imagesV1t/image-2.png)  
Que nos permite completar el ejercicio:  
![alt text](imagesV1t/image-3.png)

### Stylish Flag - Web

**Flag**: v1t{h1d30ut_css}

Es un reto de manipulación de CSS. Nos dan un URL donde al ingresar solo vemos esto.  
![alt text](imagesV1t/image-4.png)  
Si vamos al inspector, podemos ver en el html un div oculto llamado "flag".  

```html
  <h1>where is the flag ;-;</h1>
  <br>
  <div hidden="" class="flag"></div>
```

A partir de esto, podemos manipular el css en la consola para que nos muestre lo que hay en ese div. En primer lugar, lo más importante es remover el atributo "hidden". Luego de hacerlo, vemos que la flag esta pero no se ve clara. Empezamos a manipular diferentes elementos hasta que finalmente llegamos a esto, que, en resumidas cuentas, gira el div porque estaba rotado, lo posiciona en un lugar de la pantalla donde no se superponga con el h1, lo vuelve mas opaco para que se vea mejor, lo trae hasta "adelante" del todo en la pantalla, etc:

```javascript
const flag = document.querySelector('.flag');
flag.removeAttribute('hidden');
flag.style.position = 'fixed';
flag.style.top = '70%';
flag.style.left = '20%';
flag.style.transform = 'translate(-50%, -50%)';
flag.style.opacity = '1';
flag.style.background = '#000';
flag.style.border = '1px solid white';
flag.style.zIndex = '9999'; 
```

Esto nos permite ver claramente la flag:  
![alt text](imagesV1t/image-5.png)  
La ingresamos y nos da el reto resuelto:  
![alt text](imagesV1t/image-6.png)  

### Mark the lyrics - Web

**Flag**: V1T{MCK-pap-cool-ooh-yeah}

Nos dan una página donde hay letras de canciones inentendibles. Inspeccionando el código vemos que algunos elementos, aparentemente al azar, están marcados con la etiqueta `<mark></mark>`. Si reconstruimos el contenido de esas etiquetas, nos da la flag.  

![alt text](imagesV1t/image-7.png)

### Waddler - PWN

**Flag**: v1t{w4ddl3r_3x1t5_4e4d6c332b6fe62a63afe56171fd3725}

El reto consiste en conectarte a un servidor remoto donde podemos enviar algo para que nos de una respuesta. Incluyen el ejecutable que está corriendo en el servidor remoto.  
![alt text](imagesV1t/image-9.png)

Haciendo uso de las herramientas de **pwn** podemos analizar el ejecutable para ver varias cosas. Antes de eso, utilice la herramienta **strings** y al analizar la salida pude ver algunas cosas interesantes:  
![alt text](imagesV1t/image-10.png)  
Esto nos muestra que hay un archivo flag.txt al que accede el ejecutable de alguna manera, lo que nosotros debemos lograr es que llegue ahi. Seguramente haya una función que ejecute esa parte, y nosotros debemos lograr ejecutar esa función a través de un desbordamiento y sobreescribiendo la dirección de retorno. Usando **objdump** vemos una función llamada "duck" que es la que efectivamente hace eso. Lo que debemos averiguar ahora es, por un lado, el tamaño del buffer que debemos desbordar, y por otro, la dirección donde está "duck".  
Para esto si hacemos uso de **pwndgb**, ejecutando el archivo que nos brindan, y al hacer `info functions` vemos la dirección de duck. Como el ejecutable no tiene ninguna protección activada, salvo NX que para esto es indistinto, sabremos que en el servidor remoto, la función estará en el mismo lugar.  
![alt text](imagesV1t/image-11.png)  
Nos falta saber el tamaño del offset. Para esto podemos usar la herramienta **cyclic** y ver en que parte se rompe.  
![alt text](imagesV1t/image-13.png) ![alt text](imagesV1t/image-14.png)  
Con todo esto en mente, armamos el template de pwn, que está en *V1tCTF/exploit.py*, para enviar al servidor remoto. Lo ejecutamos y obtenemos la flag.  
![alt text](imagesV1t/image-12.png)

![alt text](imagesV1t/image-8.png)