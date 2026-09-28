#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// PIN DEFINITIONS
#define DS18B20_PIN 4
#define ACS712_PIN 34
#define RELAY_PIN 25

// THRESHOLDS FOR LOCAL PROTECTION
#define FAULT_TEMP 75.0
#define FAULT_CURRENT 2.5
#define FAULT_VIB_RMS 0.75

// SENSOR OBJECTS
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);
OneWire oneWire(DS18B20_PIN);
DallasTemperature tempSensor(&oneWire);

// STATE VARIABLES
bool motorRunning = true;
int faultCounter = 0;
const int SAMPLES_PER_PACKET = 64;

void setup() {
  Serial.begin(115200);
  
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Relay ON (Active Low/High depends on module. Assume HIGH=OFF, LOW=ON for safety)
  motorRunning = true;

  tempSensor.begin();
  if(!accel.begin()) {
    Serial.println("{\"error\":\"ADXL345 not found\"}");
    while(1);
  }
  accel.setRange(ADXL345_RANGE_2_G);
}

void loop() {
  // 1. Handle incoming serial commands from dashboard (bridge.py)
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == '1') {
      digitalWrite(RELAY_PIN, LOW);
      motorRunning = true;
      faultCounter = 0; // Reset protection
    } else if (cmd == '0') {
      digitalWrite(RELAY_PIN, HIGH);
      motorRunning = false;
    }
  }

  // 2. Read Temperature
  tempSensor.requestTemperatures();
  float temperature = tempSensor.getTempCByIndex(0);

  // 3. Read Current (Assuming 5V -> voltage divider -> 3.3V ADC)
  // Basic calibration: adjust offset/sensitivity as needed for your specific ACS712
  long adc_sum = 0;
  for(int i=0; i<20; i++){
    adc_sum += analogRead(ACS712_PIN);
    delay(1);
  }
  float avg_adc = adc_sum / 20.0;
  float voltage = (avg_adc / 4095.0) * 3.3;
  // Scaled calculation for 20A module through voltage divider
  float current = abs((voltage - 1.61) / 0.066); 
  if(current < 0.05) current = 0.0;

  // 4. Capture Vibration Waveform (High speed burst)
  float waveform[SAMPLES_PER_PACKET];
  float sum_sq = 0;
  
  for(int i = 0; i < SAMPLES_PER_PACKET; i++) {
    sensors_event_t event;
    accel.getEvent(&event);
    
    // Combine axes or just use Z axis. Here we use a combined magnitude proxy
    float mag = sqrt(pow(event.acceleration.x, 2) + pow(event.acceleration.y, 2) + pow(event.acceleration.z, 2)) / 9.81; // Convert m/s^2 to g
    waveform[i] = mag;
    sum_sq += pow(mag, 2);
    delay(5); // Roughly 200Hz sampling rate for this burst
  }
  
  float vib_rms = sqrt(sum_sq / SAMPLES_PER_PACKET);

  // 5. Local Hardware Protection Interlock
  if (temperature >= FAULT_TEMP || current >= FAULT_CURRENT || vib_rms >= FAULT_VIB_RMS) {
    faultCounter++;
    if (faultCounter >= 3) { // Require 3 consecutive bad readings to trip (debouncing)
      digitalWrite(RELAY_PIN, HIGH); // Trip Relay
      motorRunning = false;
    }
  } else {
    faultCounter = 0;
  }

  // 6. Construct and send JSON packet
  StaticJsonDocument<1024> doc;
  doc["timestamp"] = millis();
  doc["temperature"] = temperature;
  doc["current"] = current;
  doc["vibration_rms"] = vib_rms;
  doc["motor_state"] = motorRunning ? 1 : 0;
  
  JsonArray waveArray = doc.createNestedArray("waveform");
  for(int i=0; i<SAMPLES_PER_PACKET; i++) {
    waveArray.add(waveform[i]);
  }

  String output;
  serializeJson(doc, output);
  Serial.println(output);
}