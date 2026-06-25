#include <DHT.h>

// =====================================================
// EnerAI-Box Phase 1
// ESP32 + DHT11 + LDR + Module Relais
// Acquisition de données physiques + décision simple
// =====================================================

// -------------------------
// Configuration DHT11
// -------------------------
#define DHT_PIN 4
#define DHT_TYPE DHT11

DHT dht(DHT_PIN, DHT_TYPE);

// -------------------------
// Configuration LDR
// -------------------------
#define LDR_PIN 34

// -------------------------
// Configuration relais
// -------------------------
#define RELAY_PIN 26

// La plupart des modules relais sont actifs à LOW.
// Si ton relais fonctionne à l'envers, remplace true par false.
#define RELAY_ACTIVE_LOW true

// -------------------------
// Paramètres d'acquisition
// -------------------------
const unsigned long SAMPLE_INTERVAL_MS = 5000;
unsigned long lastSampleTime = 0;

// -------------------------
// Seuils de décision
// -------------------------
const float LIGHT_THRESHOLD_PERCENT = 50.0;
const float HIGH_TEMPERATURE_THRESHOLD = 35.0;


// =====================================================
// Fonction de commande du relais
// =====================================================
void setRelay(bool state) {
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(RELAY_PIN, state ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_PIN, state ? HIGH : LOW);
  }
}


// =====================================================
// Initialisation
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  dht.begin();

  pinMode(RELAY_PIN, OUTPUT);
  setRelay(false);

  analogReadResolution(12);              // ESP32 ADC : 0 à 4095
  analogSetPinAttenuation(LDR_PIN, ADC_11db);

  Serial.println("EnerAI-Box Phase 1 - ESP32 Data Acquisition");
  Serial.println("timestamp_ms,temperature_c,humidity_percent,light_raw,light_percent,relay_state,decision");
}


// =====================================================
// Boucle principale
// =====================================================
void loop() {
  unsigned long currentTime = millis();

  if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
    lastSampleTime = currentTime;

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    int lightRaw = analogRead(LDR_PIN);
    float lightPercent = (lightRaw / 4095.0) * 100.0;

    if (isnan(temperature) || isnan(humidity)) {
      Serial.println("ERROR,DHT_READ_FAILED");
      return;
    }

    bool solarFavorable = lightPercent >= LIGHT_THRESHOLD_PERCENT;
    bool highTemperature = temperature >= HIGH_TEMPERATURE_THRESHOLD;

    bool relayState = false;
    String decision = "";

    if (solarFavorable && !highTemperature) {
      relayState = true;
      decision = "SOLAR_FAVORABLE_LOAD_ON";
    } else if (solarFavorable && highTemperature) {
      relayState = true;
      decision = "SOLAR_AVAILABLE_HIGH_TEMP_ALERT";
    } else {
      relayState = false;
      decision = "LOW_SOLAR_ECO_MODE_LOAD_OFF";
    }

    setRelay(relayState);

    Serial.print(currentTime);
    Serial.print(",");
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.print(",");
    Serial.print(lightRaw);
    Serial.print(",");
    Serial.print(lightPercent);
    Serial.print(",");
    Serial.print(relayState ? "ON" : "OFF");
    Serial.print(",");
    Serial.println(decision);
  }
}