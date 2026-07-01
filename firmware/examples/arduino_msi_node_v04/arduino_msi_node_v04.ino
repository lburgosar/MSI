// MSI Node Alpha-01
// Version: 0.3
// Added: Event Engine

#include <DHT.h>
#include <string.h>

#define DHTPIN 2
#define DHTTYPE DHT11
#define PIN_ENERGY A0
#define MSI_ID_ENERGY       0x1001
#define MSI_ID_ENERGY_STATE 0x2001
#define MSI_ID_LOW_BATTERY  0x3001

#define MSI_MODE_STANDARD   0x01
#define MSI_TYPE_CAPABILITY 0x01
#define MSI_TYPE_STATE      0x02
#define MSI_TYPE_EVENT      0x03
#define MSI_SOF             0xAA

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

// =========================
// EVENT LAYER
// =========================

struct Events {
  bool stateChanged;
  bool lowBattery;
  bool thermalAlert;
  bool humidityLow;
};

// =========================
// GLOBAL DATA
// =========================

RawData raw;
Capabilities cap;
States state;
Events event;

const char* prevEnergyState = "UNKNOWN";
const char* prevThermalState = "UNKNOWN";
const char* prevHumidityState = "UNKNOWN";

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
// EVENT ENGINE v0.3
// =========================

void eventEngine() {
  event.stateChanged = false;
  event.lowBattery = false;
  event.thermalAlert = false;
  event.humidityLow = false;

  if (strcmp(prevEnergyState, state.energyState) != 0) {
    event.stateChanged = true;
  }

  if (strcmp(prevThermalState, state.thermalState) != 0) {
    event.stateChanged = true;
  }

  if (strcmp(prevHumidityState, state.humidityState) != 0) {
    event.stateChanged = true;
  }

  if (cap.energy < 20) {
    event.lowBattery = true;
  }

  if (strcmp(state.thermalState, "WARNING") == 0) {
    event.thermalAlert = true;
  }

  if (strcmp(state.humidityState, "LOW") == 0) {
    event.humidityLow = true;
  }

  prevEnergyState = state.energyState;
  prevThermalState = state.thermalState;
  prevHumidityState = state.humidityState;
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

void publishEvent(const char* name) {
  Serial.print("MSI_EVENT:");
  Serial.println(name);
}

byte simpleCRC(byte* data, int len) {
  byte crc = 0x00;
  for (int i = 0; i < len; i++) {
    crc ^= data[i];
  }
  return crc;
}

void printHexByte(byte b) {
  if (b < 0x10) Serial.print("0");
  Serial.print(b, HEX);
  Serial.print(" ");
}

void publishBinaryFrame(byte mode, byte type, uint16_t id, byte value) {
  byte frame[8];

  frame[0] = MSI_SOF;
  frame[1] = mode;
  frame[2] = type;
  frame[3] = 0x03;              // LEN: ID_H + ID_L + VALUE
  frame[4] = highByte(id);
  frame[5] = lowByte(id);
  frame[6] = value;
  frame[7] = simpleCRC(frame, 7);

  Serial.print("MSI_BINARY: ");
  for (int i = 0; i < 8; i++) {
    printHexByte(frame[i]);
  }
  Serial.println();
}

void transportEngine() {
  publishCapability("ENERGY", String(cap.energy));
  publishBinaryFrame(
    MSI_MODE_STANDARD,
    MSI_TYPE_CAPABILITY,
    MSI_ID_ENERGY,
    (byte)cap.energy
);
  publishCapability("TEMPERATURE", String(cap.temperature));
  publishCapability("HUMIDITY", String(cap.humidity));

  publishState("ENERGY_STATE", state.energyState);
  byte energyStateValue = 0x01;

if (strcmp(state.energyState, "WARNING") == 0) {
  energyStateValue = 0x02;
}
else if (strcmp(state.energyState, "CRITICAL") == 0) {
  energyStateValue = 0x03;
}

publishBinaryFrame(
    MSI_MODE_STANDARD,
    MSI_TYPE_STATE,
    MSI_ID_ENERGY_STATE,
    energyStateValue
);
  publishState("THERMAL_STATE", state.thermalState);
  publishState("HUMIDITY_STATE", state.humidityState);

  if (event.stateChanged) {
    publishEvent("STATE_CHANGED");
  }

  if (event.lowBattery) {
    publishEvent("LOW_BATTERY");

  publishBinaryFrame(
      MSI_MODE_STANDARD,
      MSI_TYPE_EVENT,
      MSI_ID_LOW_BATTERY,
      0x01
  );
}

  if (event.thermalAlert) {
    publishEvent("THERMAL_ALERT");
  }

  if (event.humidityLow) {
    publishEvent("HUMIDITY_LOW");
  }

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

  Serial.println("========== MSI NODE v0.3 ==========");
}

void loop() {
  acquisitionEngine();
  capabilityEngine();
  stateEngine();
  eventEngine();
  transportEngine();
  watchdogEngine();

  delay(1000);
}