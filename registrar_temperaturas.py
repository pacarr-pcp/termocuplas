"""
registrar_temperaturas.py  (v2)
Lee las líneas que manda el Arduino (termo01) por el puerto serie:
  - las muestra en consola en columnas alineadas
  - las grafica en vivo
  - las guarda en un CSV en la misma carpeta de este script

Uso:  doble clic en iniciar_registro.bat  (o: python registrar_temperaturas.py)
Para terminar: cerrar la ventana del gráfico, o Ctrl+C en la consola.
"""

import math
import os
import sys
import time
from datetime import datetime

import serial
import serial.tools.list_ports

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Falta la librería matplotlib. Instálala con:")
    print("  python -m pip install matplotlib")
    input("Enter para salir...")
    sys.exit(1)

CARPETA = os.path.dirname(os.path.abspath(__file__))
ANCHO_COLUMNA = 10         # ancho de cada columna en la consola
REPETIR_ENCABEZADO = 25    # cada cuántas filas se repite el encabezado
REFRESCO_GRAFICO = 0.5     # segundos entre redibujos del gráfico


def a_numero(txt):
    """Convierte un campo a número. 'NC' (sensor no conectado) se toma como vacío."""
    if txt.upper() == "NC":
        return float("nan")
    return float(txt)


def es_numero(txt):
    try:
        a_numero(txt)
        return True
    except ValueError:
        return False


def fila(valores):
    return "".join(f"{v:>{ANCHO_COLUMNA}}" for v in valores)


def formato_temp(x):
    return "---" if math.isnan(x) else f"{x:.2f}"


def elegir_puerto():
    puertos = list(serial.tools.list_ports.comports())
    if puertos:
        print("Puertos disponibles:")
        for p in puertos:
            print(f"  {p.device}  ({p.description})")
    else:
        print("No se detectan puertos. ¿Está conectado el Arduino?")

    if len(puertos) == 1:
        sugerido = puertos[0].device
        txt = input(f"Puerto del Arduino [Enter = {sugerido}]: ").strip().upper()
        return txt or sugerido
    return input("Puerto del Arduino (ej: COM4): ").strip().upper()


def main():
    puerto = elegir_puerto()
    baud_txt = input("Baudrate [Enter = 9600]: ").strip()
    baudrate = int(baud_txt) if baud_txt else 9600

    nombre = datetime.now().strftime("registro_%Y%m%d_%H%M%S.csv")
    ruta = os.path.join(CARPETA, nombre)

    try:
        arduino = serial.Serial(puerto, baudrate, timeout=0)
    except serial.SerialException as e:
        print(f"\nNo pude abrir {puerto}: {e}")
        print("Revisa que el Arduino esté conectado y que el Monitor Serie del IDE esté cerrado.")
        input("Enter para salir...")
        return

    print(f"\nConectado a {puerto} a {baudrate} baudios. Esperando que el Arduino reinicie...")
    time.sleep(2)

    # --- Ventana del gráfico ---
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.canvas.manager.set_window_title(f"Temperaturas - {nombre}")
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("Temperatura (°C)")
    ax.grid(True, alpha=0.3)
    plt.show(block=False)
    plt.pause(0.1)

    print(f"Guardando en: {ruta}")
    print("Presiona el pulsador para iniciar.")
    print("Para terminar: cierra la ventana del gráfico o Ctrl+C aquí.\n")

    encabezado = None
    encabezado_escrito = False
    lineas_graf = []
    xs, ys = [], []
    ultimo_t = None
    filas = 0
    buffer = b""
    hay_cambios = False
    ultimo_dibujo = 0.0

    f = open(ruta, "w", encoding="utf-8", newline="")
    try:
        while plt.fignum_exists(fig.number):
            n = arduino.in_waiting
            if n:
                buffer += arduino.read(n)
                *completas, buffer = buffer.split(b"\n")

                for crudo in completas:
                    linea = crudo.decode("utf-8", errors="ignore").strip()
                    if not linea:
                        continue
                    campos = [c.strip() for c in linea.split(",")]

                    # Línea de datos: todos los campos son números (o nan)
                    if len(campos) >= 2 and all(es_numero(c) for c in campos):
                        valores = [a_numero(c) for c in campos]

                        if encabezado is None or len(encabezado) != len(valores):
                            encabezado = ["Tiempo_s"] + [f"T{i}" for i in range(1, len(valores))]
                        if not encabezado_escrito:
                            f.write(",".join(encabezado) + "\n")
                            encabezado_escrito = True

                        f.write(linea + "\n")
                        f.flush()  # guarda al tiro, por si se corta algo

                        if filas % REPETIR_ENCABEZADO == 0:
                            print("\n" + fila(encabezado))
                        print(fila([f"{valores[0]:.2f}"] + [formato_temp(v) for v in valores[1:]]))
                        filas += 1

                        # Datos para el gráfico
                        t = valores[0]
                        if ultimo_t is not None and t < ultimo_t:
                            # el tiempo volvió a cero: nueva medición, se limpia el gráfico
                            xs.clear()
                            for y in ys:
                                y.clear()
                        ultimo_t = t

                        if not lineas_graf:
                            ys = [[] for _ in valores[1:]]
                            for nombre_serie in encabezado[1:]:
                                (ln,) = ax.plot([], [], label=nombre_serie)
                                lineas_graf.append(ln)
                            ax.legend(loc="upper left")

                        xs.append(t)
                        for y, v in zip(ys, valores[1:]):
                            y.append(v)
                        hay_cambios = True

                    # Encabezado enviado por el Arduino (todo texto, varias columnas)
                    elif len(campos) >= 2 and not any(es_numero(c) for c in campos):
                        encabezado = campos
                        if not encabezado_escrito:
                            f.write(linea + "\n")
                            encabezado_escrito = True

                    # Cualquier otro mensaje del Arduino
                    else:
                        print(f"[Arduino] {linea}")

            # Redibujar el gráfico cada cierto tiempo
            if hay_cambios and time.time() - ultimo_dibujo > REFRESCO_GRAFICO:
                for ln, y in zip(lineas_graf, ys):
                    ln.set_data(xs, y)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw_idle()
                hay_cambios = False
                ultimo_dibujo = time.time()

            fig.canvas.flush_events()
            time.sleep(0.05)

    except KeyboardInterrupt:
        pass
    finally:
        f.close()
        arduino.close()
        print(f"\nRegistro detenido. {filas} filas guardadas en:\n  {ruta}")


if __name__ == "__main__":
    main()
