#include <SPI.h>

// Un pin CS por modulo MAX6675. SO (pin 12) y SCK (pin 13) son compartidos (bus SPI).
const uint8_t CS_PINS[] = {10, 9, 8, 7, 6};
const uint8_t NUM_SENSORS = sizeof(CS_PINS) / sizeof(CS_PINS[0]);

const uint8_t BUTTON_PIN = 2;                   // pulsador entre este pin y GND (usa pull-up interno)
const uint8_t LED_PIN = 4;                      // LED indicador: encendido mientras registra
const unsigned long SAMPLE_INTERVAL_MS = 250;   // periodo de muestreo (minimo recomendado para el MAX6675, ~220 ms por conversion)
const unsigned long DEBOUNCE_MS = 50;

SPISettings max6675_spi(4000000, MSBFIRST, SPI_MODE0);

bool logging = false;
unsigned long loggingStartTime = 0;
unsigned long lastSampleTime = 0;

bool lastButtonReading = HIGH;
unsigned long lastDebounceTime = 0;

bool readMAX6675(uint8_t csPin, double &temperatureC) {
  SPI.beginTransaction(max6675_spi);
  digitalWrite(csPin, LOW);
  delayMicroseconds(10);

  uint16_t data = SPI.transfer16(0x00);

  digitalWrite(csPin, HIGH);
  SPI.endTransaction();

  if (data & 0x4) {
    return false;  // termocupla no conectada / abierta
  }

  data >>= 3;
  temperatureC = data * 0.25;
  return true;
}

void printHeader() {
  Serial.print("Tiempo_s");
  for (uint8_t i = 0; i < NUM_SENSORS; i++) {
    Serial.print(",S");
    Serial.print(i + 1);
  }
  Serial.println();
}

void logRow() {
  double elapsedS = (millis() - loggingStartTime) / 1000.0;
  Serial.print(elapsedS, 3);

  for (uint8_t i = 0; i < NUM_SENSORS; i++) {
    double temperature;
    Serial.print(",");
    if (readMAX6675(CS_PINS[i], temperature)) {
      Serial.print(temperature, 2);
    } else {
      Serial.print("NC");
    }
  }
  Serial.println();
}

// Pulsador momentaneo: cada flanco de bajada alterna inicio/parada del registro.
void handleButton() {
  bool reading = digitalRead(BUTTON_PIN);

  if (reading != lastButtonReading) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > DEBOUNCE_MS) {
    static bool buttonState = HIGH;
    if (reading != buttonState) {
      buttonState = reading;
      if (buttonState == LOW) {
        logging = !logging;
        if (logging) {
          loggingStartTime = millis();
          lastSampleTime = loggingStartTime - SAMPLE_INTERVAL_MS;  // primer muestreo inmediato
          printHeader();
        } else {
          Serial.println("--- registro detenido ---");
        }
      }
    }
  }

  lastButtonReading = reading;
}

void setup() {
  Serial.begin(9600);

  for (uint8_t i = 0; i < NUM_SENSORS; i++) {
    pinMode(CS_PINS[i], OUTPUT);
    digitalWrite(CS_PINS[i], HIGH);
  }

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  SPI.begin();

  Serial.println("Presiona el switch para iniciar el registro...");
}

void loop() {
  handleButton();

  digitalWrite(LED_PIN, logging ? HIGH : LOW);

  if (logging && (millis() - lastSampleTime >= SAMPLE_INTERVAL_MS)) {
    lastSampleTime += SAMPLE_INTERVAL_MS;
    logRow();
  }
}
