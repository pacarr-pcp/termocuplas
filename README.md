# termo01 — Registrador de temperaturas con Arduino

Registro de **5 termocuplas tipo K** con módulos **MAX6675** y un **Arduino UNO**.
Las lecturas se envían por USB a un PC, donde un script en Python las muestra en una tabla,
las grafica en vivo y las guarda en un archivo CSV listo para abrir en Excel.

Pensado para mediciones en terreno, con todo montado dentro de una caja con un pulsador y un LED indicador.

## Archivos

| Archivo | Descripción |
|---|---|
| `termo01/termo01.ino` | Sketch del Arduino: lee los 5 sensores cada 250 ms y envía los datos por Serial |
| `registrar_temperaturas.py` | Script de Python: tabla en consola, gráfico en vivo y guardado en CSV |
| `iniciar_registro.bat` | Acceso directo para Windows: inicia el script con doble clic |

## Materiales

- Arduino UNO (original o clon con chip CH340)
- 5 módulos MAX6675 con termocupla tipo K
- 1 pulsador momentáneo
- 1 LED + resistencia de 220–330 Ω
- Cable USB y PC con Windows

## Conexiones

Los módulos comparten el bus SPI: todo va en paralelo excepto el pin **CS**, que es uno por módulo.

| Módulo MAX6675 | Arduino UNO |
|---|---|
| VCC (los 5) | 5V |
| GND (los 5) | GND |
| SO (los 5) | Pin 12 |
| SCK (los 5) | Pin 13 |
| CS sensor 1 … 5 | Pines 10, 9, 8, 7, 6 |

| Otro componente | Conexión |
|---|---|
| Pulsador | Entre pin 2 y GND (usa el pull-up interno) |
| LED | Pin 4 → resistencia → LED → GND |

El pin 11 no se usa: el MAX6675 es de solo lectura.

## Instalación en el PC (una sola vez)

1. Instalar [Python 3](https://www.python.org/downloads/).
2. Abrir una consola (`cmd`) e instalar las librerías:
   ```
   python -m pip install pyserial matplotlib
   ```
3. Cargar `termo01/termo01.ino` en el Arduino con el IDE de Arduino.
4. Si Windows no reconoce la placa, instalar el driver CH340.

## Uso

1. Conectar el Arduino por USB.
2. Doble clic en `iniciar_registro.bat`.
3. Elegir el puerto COM (si hay uno solo, basta con Enter) y el baudrate (Enter = 9600).
4. Presionar el pulsador para iniciar: el LED se enciende y comienzan las lecturas.
5. Presionar de nuevo para detener. Para cerrar el programa, cerrar la ventana del gráfico o usar Ctrl+C.

Cada sesión genera un archivo `registro_AAAAMMDD_HHMMSS.csv` en la misma carpeta del script.
Un sensor desconectado aparece como `NC` en el CSV y como `---` en pantalla.

## Notas

- El intervalo mínimo recomendado es **250 ms**: el MAX6675 tarda unos 220 ms en cada conversión,
  y leerlo más seguido entrega valores repetidos.
- El Monitor Serie del IDE de Arduino debe estar cerrado mientras corre el script
  (solo un programa puede usar el puerto a la vez).
