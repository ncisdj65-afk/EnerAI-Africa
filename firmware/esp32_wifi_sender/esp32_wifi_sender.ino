
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
// =====================================================
// EnerAI-Box Phase 2
// ESP32 + DHT11 + LDR + Relay + Wi-Fi HTTP POST
// =====================================================

// -------------------------
// Wi-Fi configuration
// -------------------------
#include "arduino_secrets.h"



// =====================================================
// EnerAI-Box Phase 3B
// ESP32 + DHT11 + LDR + Relay + Wi-Fi API Control
// The Python API computes the energy decision.
// The ESP32 applies the returned relay command.
// =====================================================



// -------------------------
// Device ID
// -------------------------
const char* DEVICE_ID = "enerai_box_esp32_001";

// -------------------------
// DHT11 configuration
// -------------------------
#define DHT_PIN 4
#define DHT_TYPE DHT11
#define STATUS_LED_PIN 25

DHT dht(DHT_PIN, DHT_TYPE);

// -------------------------
// LDR configuration
// -------------------------
#define LDR_PIN 34

// -------------------------
// Relay configuration
// -------------------------
#define RELAY_PIN 26

// Beaucoup de modules relais sont actifs à LOW.
// Si ton relais fonctionne à l'envers, remplace true par false.
#define RELAY_ACTIVE_LOW true

// -------------------------
// Acquisition parameters
// -------------------------
const unsigned long SAMPLE_INTERVAL_MS = 10000;
unsigned long lastSampleTime = 0;

// État actuel du relais côté ESP32
String currentRelayState = "OFF";
String lastPythonDecision = "NO_DECISION_YET";


// =====================================================
// Relay control
// =====================================================
void setRelay(bool state) {
  if (RELAY_ACTIVE_LOW) {
    digitalWrite(RELAY_PIN, state ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_PIN, state ? HIGH : LOW);
  }

  digitalWrite(STATUS_LED_PIN, state ? HIGH : LOW);

  currentRelayState = state ? "ON" : "OFF";
}



// =====================================================
// Apply command returned by Python API
// =====================================================
void applyRelayCommand(String relayCommand) {
  relayCommand.trim();
  relayCommand.toUpperCase();

  if (relayCommand == "ON") {
    setRelay(true);
    Serial.println("Relay command applied: ON");
  } else if (relayCommand == "OFF") {
    setRelay(false);
    Serial.println("Relay command applied: OFF");
  } else {
    Serial.print("Unknown relay command received: ");
    Serial.println(relayCommand);
    Serial.println("Keeping previous relay state.");
  }
}


// =====================================================
// Wi-Fi connection
// =====================================================
void connectToWiFi() {
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempt = 0;

  while (WiFi.status() != WL_CONNECTED && attempt < 30) {
    delay(500);
    Serial.print(".");
    attempt++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Wi-Fi connected");
    Serial.print("ESP32 IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi connection failed");
  }
}


// =====================================================
// Send data to Python API and apply returned decision
// =====================================================
void sendSensorDataToApi(
  float temperature,
  float humidity,
  int lightRaw,
  float lightPercent
) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi disconnected. Reconnecting...");
    connectToWiFi();

    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("Cannot send data: Wi-Fi unavailable");
      return;
    }
  }

  HTTPClient http;

  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"device_id\":\"" + String(DEVICE_ID) + "\",";
  payload += "\"temperature_c\":" + String(temperature, 2) + ",";
  payload += "\"humidity_percent\":" + String(humidity, 2) + ",";
  payload += "\"light_raw\":" + String(lightRaw) + ",";
  payload += "\"light_percent\":" + String(lightPercent, 2) + ",";
  payload += "\"relay_state\":\"" + currentRelayState + "\",";
  payload += "\"decision\":\"" + lastPythonDecision + "\"";
  payload += "}";

  Serial.println();
  Serial.print("Sending payload: ");
  Serial.println(payload);

  int httpResponseCode = http.POST(payload);

  Serial.print("HTTP response code: ");
  Serial.println(httpResponseCode);

  if (httpResponseCode > 0) {
    String response = http.getString();

    Serial.print("API response: ");
    Serial.println(response);

    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, response);

    if (error) {
      Serial.print("JSON parsing failed: ");
      Serial.println(error.c_str());
      http.end();
      return;
    }

    const char* relayCommand = doc["relay_command"] | "UNKNOWN";
    const char* energyMode = doc["energy_mode"] | "UNKNOWN";
    const char* decision = doc["decision"] | "UNKNOWN";
    const char* priority = doc["priority"] | "UNKNOWN";

    lastPythonDecision = String(decision);

    Serial.print("Python relay_command: ");
    Serial.println(relayCommand);

    Serial.print("Python energy_mode: ");
    Serial.println(energyMode);

    Serial.print("Python decision: ");
    Serial.println(decision);

    Serial.print("Python priority: ");
    Serial.println(priority);

    applyRelayCommand(String(relayCommand));

  } else {
    Serial.print("HTTP POST failed. Error: ");
    Serial.println(http.errorToString(httpResponseCode));
  }

  http.end();
}


// =====================================================
// Setup
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  dht.begin();

  pinMode(RELAY_PIN, OUTPUT);
  setRelay(false);
  pinMode(STATUS_LED_PIN, OUTPUT);
digitalWrite(STATUS_LED_PIN, LOW);

  analogReadResolution(12);
  analogSetPinAttenuation(LDR_PIN, ADC_11db);

  Serial.println("EnerAI-Box Phase 3B - API Controlled Relay");
  Serial.println("timestamp_ms,temperature_c,humidity_percent,light_raw,light_percent,current_relay_state,last_python_decision");

  connectToWiFi();
}


// =====================================================
// Main loop
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
    Serial.print(currentRelayState);
    Serial.print(",");
    Serial.println(lastPythonDecision);

    sendSensorDataToApi(
      temperature,
      humidity,
      lightRaw,
      lightPercent
    );
  }
}