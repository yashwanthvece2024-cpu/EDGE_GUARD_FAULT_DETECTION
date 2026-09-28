#include <Wire.h>
#include <Adafruit_ADXL345_U.h>
#include <OneWire.h>
#include <DallasTemperature.h>


// =====================================================
// PINS
// =====================================================

#define DS18B20_PIN 4
#define ACS712_PIN 34
#define RELAY_PIN 25

#define SDA_PIN 21
#define SCL_PIN 22


// =====================================================
// OBJECTS
// =====================================================

Adafruit_ADXL345_Unified accel =
    Adafruit_ADXL345_Unified(12345);

OneWire oneWire(DS18B20_PIN);

DallasTemperature tempSensor(
    &oneWire
);


// =====================================================
// SETTINGS
// =====================================================

const float ACS712_ZERO_VOLTAGE = 2.5;

// Change this according to your exact ACS712 version.
// 185mV/A = ACS712 5A
// 100mV/A = ACS712 20A
// 66mV/A  = ACS712 30A

const float ACS712_SENSITIVITY = 0.185;


// =====================================================
// SETUP
// =====================================================

void setup()
{
    Serial.begin(115200);

    Wire.begin(
        SDA_PIN,
        SCL_PIN
    );

    tempSensor.begin();

    pinMode(
        RELAY_PIN,
        OUTPUT
    );

    digitalWrite(
        RELAY_PIN,
        HIGH
    );

    if (!accel.begin())
    {
        Serial.println(
            "{\"error\":\"ADXL345 not detected\"}"
        );
    }

    accel.setRange(
        ADXL345_RANGE_16_G
    );

    delay(1000);
}


// =====================================================
// TEMPERATURE
// =====================================================

float readTemperature()
{
    tempSensor.requestTemperatures();

    return tempSensor.getTempCByIndex(0);
}


// =====================================================
// CURRENT
// =====================================================

float readCurrent()
{
    int raw = analogRead(
        ACS712_PIN
    );

    float voltage =
        (raw / 4095.0) * 3.3;

    // This assumes the ACS712 output has
    // been safely conditioned for ESP32 ADC input.

    float current =
        abs(
            (voltage - ACS712_ZERO_VOLTAGE)
            / ACS712_SENSITIVITY
        );

    return current;
}


// =====================================================
// VIBRATION
// =====================================================

float readVibration()
{
    sensors_event_t event;

    accel.getEvent(
        &event
    );

    float x = event.acceleration.x / 9.80665;
    float y = event.acceleration.y / 9.80665;
    float z = event.acceleration.z / 9.80665;

    float magnitude =
        sqrt(
            x*x +
            y*y +
            z*z
        );

    return magnitude;
}


// =====================================================
// LOOP
// =====================================================

void loop()
{
    float temperature =
        readTemperature();

    float current =
        readCurrent();

    float vibration =
        readVibration();


    int motorState =
        digitalRead(RELAY_PIN);


    Serial.print("{");

    Serial.print(
        "\"temperature\":"
    );

    Serial.print(
        temperature,
        2
    );


    Serial.print(
        ",\"current\":"
    );

    Serial.print(
        current,
        2
    );


    Serial.print(
        ",\"vibration_rms\":"
    );

    Serial.print(
        vibration,
        3
    );


    Serial.print(
        ",\"motor_state\":"
    );

    Serial.print(
        motorState ? 1 : 0
    );


    Serial.println(
        "}"
    );


    delay(1000);
}