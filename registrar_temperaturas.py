import csv
import datetime
import sys

import serial

BAUDRATE = 9600  # debe coincidir con Serial.begin(9600) del Arduino


def main():
    port = input("Puerto COM del Arduino (ej: COM3): ").strip()

    try:
        ser = serial.Serial(port, BAUDRATE, timeout=2)
    except serial.SerialException as e:
        print(f"No se pudo abrir el puerto {port}: {e}")
        sys.exit(1)

    filename = f"registro_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    print(f"Conectado a {port}. Guardando en {filename}")
    print("El Arduino puede reiniciarse solo al abrir el puerto, esperá unos 2 segundos y apretá el pulsador.")
    print("Ctrl+C para detener el registro.\n")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        try:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                print(line)
                writer.writerow(line.split(","))
                f.flush()
        except KeyboardInterrupt:
            print("\nRegistro detenido.")
        finally:
            ser.close()


if __name__ == "__main__":
    main()
