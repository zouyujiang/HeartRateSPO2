#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

MAX30105 particleSensor;

void setup() {
  Serial.begin(115200);  // initialize serial communication at 115200 bits per second:

  // Initialize sensor
  while (!particleSensor.begin(Wire, I2C_SPEED_FAST))  //Use default I2C port, 400kHz speed
  {
    delay(3000);
    Serial.println(F("[LOG] Sensor connection failed!"));
    particleSensor.begin(Wire, I2C_SPEED_FAST);
  }

  byte ledBrightness = 240;  //Options: 0=Off to 255=50mA
  byte sampleAverage = 4;   //Options: 1, 2, 4, 8, 16, 32
  byte ledMode = 2;         //Options: 1 = Red only, 2 = Red + IR, 3 = Red + IR + Green
  byte sampleRate = 200;    //Options: 50, 100, 200, 400, 800, 1000, 1600, 3200
  int pulseWidth = 411;     //Options: 69, 118, 215, 411
  int adcRange = 16384;      //Options: 2048, 4096, 8192, 16384

  particleSensor.setup(ledBrightness, sampleAverage, ledMode, sampleRate, pulseWidth, adcRange);  //Configure sensor with these settings
  particleSensor.enableDIETEMPRDY();                                                              //Enable the temp ready interrupt. This is required.
}

void loop() {
  //dumping the first 25 sets of samples in the memory and shift the last 75 sets of samples to the top
  while (particleSensor.available() == false)  //do we have new data?
    particleSensor.check();                    //Check the sensor for new data
  particleSensor.nextSample();                 //We're finished with this sample so move to next sample
  float temperature = particleSensor.readTemperature();
  //send samples and calculation result to terminal program through UART
  Serial.print("[DATA] ");
  Serial.print("temperatureC=");
  Serial.print(temperature, 4);

  Serial.print(F(",red="));
  Serial.print(particleSensor.getRed(), DEC);
  Serial.print(F(",ir="));
  Serial.print(particleSensor.getIR(), DEC);

  Serial.print(F(",time="));
  Serial.println(millis());
}
