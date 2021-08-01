#include <Arduino.h>
#include <TM1637Display.h>
/*
  - Serial 추가
  - sensor값? (0~5) 또는 스케일된 값.
*/

#define CLK 2
#define DIO 3
#define PRESSURE A0

TM1637Display dsp(CLK, DIO);

float sensorMin = 2.420;
float sensorMax = 4.250;
int hysteresis_value = 2;

float MIN = 2.120;

float sensorVal;
float pressDisp;

int calcPressDisp(){
  sensorVal = (int)(analogRead(PRESSURE) * 100);
  return sensorVal;
}

void showDisp(){
  dsp.showNumberDec(calcPressDisp());
}

void setup(){
  pinMode(PRESSURE, INPUT);

  dsp.setBrightness(2);
}

void loop(){
  showDisp();
  delay(50);
}
