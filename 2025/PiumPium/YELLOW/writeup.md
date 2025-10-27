# 🕵 Writeup - Yellow (Steganography Challenge)

*Categoría:* Stego  
*Autor:* NoRelect  
*Puntos:* 100  

---

## 🟡 Descripción

> Dedicated this challenge to a person that I love whose favorite color is yellow :)

Se nos entrega una imagen llamada yellow.png. El texto hace referencia al color amarillo, por lo que probablemente la imagen sea completamente amarilla o contenga información oculta en su estructura interna.

---

## 🔍 Análisis inicial

Abrimos la imagen y notamos que *toda la imagen es de color amarillo sólido (RGB: 255, 255, 0)*.  
Por lo tanto, *no hay información visual oculta en los píxeles*, descartando métodos LSB.

El siguiente paso fue inspeccionar los *chunks del formato PNG*.  
Un archivo PNG está compuesto por bloques (chunks) como:

- IHDR: encabezado
- IDAT: datos de la imagen
- IEND: fin del archivo

---

## 🧩 Extracción de los datos ocultos

Al analizar los chunks del PNG, se observó algo inusual:
había **muchos chunks IDAT*, y sus **longitudes* parecían formar un patrón.

Ejemplo de las longitudes:
[111, 112, 101, 110, 69, 67, 83, 67, 123, 87, 51, 95, 52, 108, 49, 95, 108, 49, 118, 51, 95, 49, 110, 95, 52, 95, 121, 51, 108, 108, 48, 119, 95, 115, 117, 98, 109, 52, 114, 49, 110, 51, 125]

Si convertimos cada número a su *carácter ASCII equivalente*, obtenemos:
openECSC{W3_4l1_l1v3_1n_4_y3ll0w_subm4r1n3}

---

## 🎯 Flag
openECSC{W3_4l1_l1v3_1n_4_y3ll0w_subm4r1n3}

