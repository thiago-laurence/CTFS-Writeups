# 🔗 Challenge 3: Chain Clue

**Categoría:** Blockchain Forensics / OSINT  
**Dificultad:** Fácil  
**Red:** Sepolia Testnet

## 📝 Descripción
El desafío proporcionaba información sobre una transacción en la red de pruebas de Ethereum (Sepolia) y el objetivo era recuperar información oculta dentro de la misma.

**Datos proporcionados:**
* **Transaction Hash:** `0x1c1e14180c2e5dceefc260208199e23a8c61524dd54bd2e378cee00e14555c14`
* **Contract Address:** `0xFb67326dAacdD9163c0eeEB9E429D7D4B6c4EBb1`

## 🕵️‍♂️ Análisis y Resolución

### 1. Exploración de la Blockchain
Para analizar los datos crudos de la transacción, se utilizó un explorador de bloques estándar para la red Sepolia.
* **Herramienta:** Etherscan (Sepolia)
* **Acción:** Se realizó una búsqueda utilizando el *Transaction Hash* proporcionado en `sepolia.etherscan.io`.

### 2. Inspección del Payload (Input Data)
En la arquitectura de Ethereum, las transacciones pueden llevar datos arbitrarios en el campo `Input Data` (a menudo usado para parámetros de funciones o mensajes).

1.  Al cargar los detalles de la transacción, se localizó la sección **"More Details"**.
2.  Se identificó el campo **Input Data**, el cual contenía una larga cadena de datos en formato Hexadecimal.

### 3. Decodificación
La cadena hexadecimal no era legible a simple vista. Se procedió a decodificarla para revelar su contenido ASCII/UTF-8.

* **Método:** Utilizando la función nativa de Etherscan "View Input As -> UTF-8",  a su vez se desarrollo un script en python donde se automatice todo esto mencionado para la resolucion del challenge.
* **Resultado:** El hexadecimal se tradujo a texto plano, revelando la flag directamente.

## 🚩 Flag
> `nexus{Tr4c3_Th3_Tr4ns4ct10n}`

