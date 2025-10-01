# Desafío: regex-auth
- **Categoría**: Web
- **Flag**: fwectf{emp7y_regex_m47che5_every7h1ng}

Para este desafío analizamos el código fuente provisto y los valores almacenados en la web.
Por cada sesión se guardan cookies con los valores de username y uid. El campo uid está codificado en base64 y formateado a partir de la combinación del rol del usuario, y un id generado de forma aleatoria.  
Inspeccionando el código fuente se ve la función que evalúa el rol del usuario:
![codigo_fuente](/CTFS-Writeups/2025/DeSAuth/regex-aux/regex-auth.png)

Con este dato, podemos deducir que si modificamos el uid almacenado en la cookie, 
agregando como prefijo un valor codificado en base 64 diferente a los correspondientes a la 
expresión regular “user*” o “guest*”, es posible ejecutar el segundo elif y hacer que la 
página imprima la flag: 

- Modificamos la cookie y recargamos la página:
![codigo_flag](/CTFS-Writeups/2025/DeSAuth/regex-aux/regex-flag.png)

- Con eso obtuvimos la flag y pudimos ingresarla en el CTF:  
![score](/CTFS-Writeups/2025/DeSAuth/regex-aux/regex-correct.png)
![score](/CTFS-Writeups/2025/DeSAuth/regex-aux/regex-score.png)