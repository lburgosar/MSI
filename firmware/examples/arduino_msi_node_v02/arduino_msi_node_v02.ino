#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT11
#define PIN_ENERGY A0

DHT dht(DHTPIN, DHTTYPE);

// =========================
// RAW DATA LAYER
// =========================

struct RawData {
  int energyRaw;
  float temperature;
  float humidity;
};

// =========================
// CAPABILITY LAYER
// =========================

struct Capabilities {
  int energy;
  float temperature;
  float humidity;
};

// =========================
// STATE LAYER
// =========================

struct States {
  const char* energyState;
  const char* thermalState;
  const char* humidityState;
};

RawData raw;
Capabilities cap;
States state;

// =========================
// ACQUISITION ENGINE
// =========================

void acquisitionEngine() {
  raw.energyRaw = analogRead(PIN_ENERGY);
  raw.temperature = dht.readTemperature();
  raw.humidity = dht.readHumidity();
}

// =========================
// CAPABILITY ENGINE
// =========================

void capabilityEngine() {
  cap.energy = map(raw.energyRaw, 0, 1023, 0, 100);

  if (!isnan(raw.temperature)) {
    cap.temperature = raw.temperature;
  }

  if (!isnan(raw.humidity)) {
    cap.humidity = raw.humidity;
  }
}

// =========================
// STATE ENGINE
// =========================

void stateEngine() {
  if (cap.energy < 20) {
    state.energyState = "CRITICAL";
  } else if (cap.energy < 40) {
    state.energyState = "WARNING";
  } else {
    state.energyState = "NORMAL";
  }

  if (cap.temperature > 35) {
    state.thermalState = "WARNING";
  } else {
    state.thermalState = "NORMAL";
  }

  if (cap.humidity < 30) {
    state.humidityState = "LOW";
  } else {
    state.humidityState = "NORMAL";
  }
}

// =========================
// TRANSPORT ENGINE
// =========================

void publishCapability(const char* name, String value) {
  Serial.print("MSI_CAPABILITY:");
  Serial.print(name);
  Serial.print("=");
  Serial.println(value);
}

void publishState(const char* name, const char* value) {
  Serial.print("MSI_STATE:");
  Serial.print(name);
  Serial.print("=");
  Serial.println(value);
}

void transportEngine() {
  publishCapability("ENERGY", String(cap.energy));
  publishCapability("TEMPERATURE", String(cap.temperature));
  publishCapability("HUMIDITY", String(cap.humidity));

  publishState("ENERGY_STATE", state.energyState);
  publishState("THERMAL_STATE", state.thermalState);
  publishState("HUMIDITY_STATE", state.humidityState);

  Serial.println("--------------------");
}

// =========================
// WATCHDOG ENGINE v0.1
// =========================

void watchdogEngine() {
  if (cap.energy <= 5) {
    Serial.println("MSI_EVENT:SAFE_MODE_REQUIRED");
  }
}

// =========================
// SETUP / LOOP
// =========================

void setup() {
  Serial.begin(115200);
  dht.begin();

  Serial.println("========== MSI NODE v0.2 ==========");
}

void loop() {
  acquisitionEngine();
  capabilityEngine();
  stateEngine();
  transportEngine();
  watchdogEngine();

  delay(1000);
}