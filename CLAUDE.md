# CLAUDE.md — Proyecto termo01

Contexto para Claude Code. Responder en español (Chile), explicaciones simples:
el usuario es ingeniero de procesos, no programador. Antes de cambios grandes,
explicar las opciones y esperar confirmación.

## Qué es

Registrador de temperaturas para mediciones en terreno (todo montado en una caja).
Un Arduino UNO lee 5 termocuplas con módulos MAX6675 y envía los datos por USB/Serial.
En el PC, un script de Python los muestra en tabla, los grafica en vivo y los guarda en CSV.

## Archivos

- `termo01/termo01.ino` — sketch del Arduino (versión final en uso).
- `registrar_temperaturas.py` — script del PC (pyserial + matplotlib).
- `iniciar_registro.bat` — inicia el script con doble clic en Windows.
- `README.md` — documentación pública (también está en GitHub).

## Hardware

- Placa: Arduino UNO clon chino (chip USB CH340). En el PC de pruebas quedó en COM4.
- Bus SPI compartido: VCC→5V, GND común, SO→pin 12, SCK→pin 13. Pin 11 (MOSI) no se usa.
- CS de cada módulo: pines 10, 9, 8, 7, 6 (sensores S1…S5).
- Pulsador momentáneo entre pin 2 y GND (INPUT_PULLUP). Cada pulsación alterna inicio/parada.
- LED indicador en pin 4 (con resistencia 220–330 Ω): encendido mientras registra.
- Consumo total de los 5 módulos: ~20–40 mA, sin riesgo para el UNO.
- Si algún día se usa una Arduino Mega: el SPI por hardware está en MISO=50, SCK=52 (hay que recablear).

## Protocolo Serial (9600 baudios)

- Al iniciar el registro, el Arduino envía el encabezado: `Tiempo_s,S1,S2,S3,S4,S5`
- Luego una línea cada 250 ms: `0.000,24.50,25.00,NC,23.25,24.00`
  - `Tiempo_s` con 3 decimales, parte de 0 en cada inicio.
  - `NC` = termocupla desconectada/abierta.
- Al detener: `--- registro detenido ---`

## Decisiones tomadas

- Intervalo de 250 ms: el MAX6675 tarda ~220 ms por conversión; leerlo más seguido
  (el usuario pidió 100 ms) entrega valores repetidos. Más rápido requeriría otro chip.
- Solo se registra el tiempo en segundos del Arduino (sin fecha/hora del PC por fila).
- El puerto COM se pide por teclado (lista los puertos; si hay uno solo, Enter lo elige).
- El CSV se guarda junto al script: `registro_AAAAMMDD_HHMMSS.csv`, escrito línea a línea
  (flush) para no perder datos si se corta algo.
- En consola los valores se muestran tabulados; el CSV queda separado por comas para Excel.
- El gráfico se limpia cuando el tiempo vuelve a 0 (nueva medición con el pulsador).
- Se evaluó Microsoft Data Streamer (Excel 365) como alternativa; se prefirió el script.

## Entorno del PC

- Windows, Python 3.14, comando `python`.
- Librerías: `python -m pip install pyserial matplotlib`
- El Monitor Serie del IDE de Arduino debe estar cerrado mientras corre el script.

## Ideas pendientes (no hechas)

- Ventana con botones (tkinter) en vez de consola: elegir COM, conectar/detener,
  temperaturas actuales en grande, gráfico integrado.
