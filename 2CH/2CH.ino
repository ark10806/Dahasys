#include <Arduino.h>
#include <TM1637Display.h>
#include <EEPROM.h>

#define PRESSURE A0

#define MD 7
#define UP 8
#define DN 9

#define CLK 2                       // segments pin1
#define DIO 3                       // segments pin2

//#define PWM_OUTPUT 9      //to send pressure data to other device

#define LED_G 4
#define LED_R 6

#define TERM 30
#define INPUT_TERM 300
#define goOnTERM 50

#define NORMAL HIGH
#define ABNORMAL LOW

//############### Setting value at factory initialization########
#define ch0_PREFIX 50
#define ch1_PREFIX 70
//###############################################################
 

int ch0;
int ch1;
bool sensor_low_bound_bool = 0;
bool sensor_high_bound_bool = 0;

//##################################################################################
#define SERIAL_TERM 100
//##################################################################################
float sensorMin = 2.520;
float sensorMax = 4.250;
int hysteresis_value = 2;
//==================================================================================
 bool display_onoff = 1;                                    // display show 
//==================================================================================
TM1637Display dsp(CLK, DIO);


const uint8_t SEG_VAL_D[] = {SEG_B | SEG_C | SEG_D | SEG_E | SEG_G}; // d
const uint8_t SEG_VAL_S[] = {SEG_A | SEG_F | SEG_G | SEG_C | SEG_D};
const uint8_t SEG_VAL_A[] = {SEG_A | SEG_F | SEG_B | SEG_G | SEG_E | SEG_C};
const uint8_t SEG_VAL_V[] = {SEG_F | SEG_B | SEG_E | SEG_C | SEG_D};

const uint8_t SEG_VAL_P[] = {SEG_A | SEG_F | SEG_E | SEG_G | SEG_B};
const uint8_t SEG_VAL_C[] = {SEG_A | SEG_F | SEG_E | SEG_D};
const uint8_t SEG_VAL_L[] = {SEG_F | SEG_E | SEG_D};
const uint8_t SEG_VAL_H[] = {SEG_F | SEG_E | SEG_G | SEG_B | SEG_C};

bool prevArr[] = {false, false, false}; // MD, UP, DN
bool currArr[] = {false, false, false};
bool btnState[] = {false, false, false};
int btnIdx;

float sensorVal;
float pressDisp;

float pressArr[] = {0, 0, 0, 0, 0};
int circularIdx = 0;
float pressAvg;

int pwmOutput;
bool control_hysteresis_bool = 1;

bool goOn = false;
long startTime;
long VsetTime = 5000;
bool isInit = true;

void setPrefix(){
      dsp.setSegments(SEG_VAL_L,1,1);
      dsp.setSegments(SEG_VAL_S,1,2);
      dsp.setSegments(SEG_VAL_C,1,3);
  delay(3000);
  while(!btnState[MD-7]){
    btnCheck(MD);
    dsp.setSegments(SEG_VAL_L,1,1);
    dsp.setSegments(SEG_VAL_S,1,2);
    dsp.setSegments(SEG_VAL_C,1,3);
  }
  
  dsp.setSegments(SEG_VAL_P,1,1);
  dsp.setSegments(SEG_VAL_S,1,2);
  dsp.setSegments(SEG_VAL_C,1,3);
  sensorMax = (float)analogRead(PRESSURE) / 1024 * 5;
  EEPROM.write(10, sensorMax);
  delay(2000);
  btnState[MD-7] = false;
}

void btnCheck(int btn){
  btnIdx = btn - 7;
  currArr[btnIdx] = digitalRead(btn);
  if(!prevArr[btnIdx] && currArr[btnIdx]){
    btnState[btnIdx] = true;
    if(btn == 7){
      startTime = millis();
      while(millis() - startTime < VsetTime){
        if(!digitalRead(btn))
          return;
      }
//      if(sensorMin == MIN){
      sensorMin = (float)analogRead(PRESSURE)/1024*5;
      EEPROM.put(0, sensorMin);
      delay(100);
    btnState[btnIdx] = false;
        setPrefix();
//      }
//      else{
//        sensorMax = (float)analogRead(PRESSURE)/1024*5;
//        MIN = sensorMin;
//      }
    }
  }
  else if(prevArr[btnIdx] && currArr[btnIdx] && btn>7){
    btnState[btnIdx] = true;
    startTime = millis();
    long setTime = 500;
    while(millis() - startTime < setTime){
      if(!digitalRead(btn))
        return;
    }
    goOn = true;
  }
  if(!digitalRead(btn))
    btnState[btnIdx] = false;
   prevArr[btnIdx] = currArr[btnIdx];
}

void pressCheck(){
  int sensor_pressure = calcPressDisp();
  if(sensor_pressure >= ch0 && sensor_pressure <= ch1){ // 2
  sensor_low_bound_bool = 1;
  sensor_high_bound_bool = 1;
  digitalWrite(LED_G,HIGH);
  digitalWrite(LED_R,LOW);
  
  }else if(sensor_pressure >= ch0-2 && sensor_pressure <= ch1 && sensor_low_bound_bool){
  digitalWrite(LED_G,HIGH);
  digitalWrite(LED_R,LOW);
  
  }else if(sensor_pressure < ch0-2){
  sensor_low_bound_bool = 0;
  digitalWrite(LED_G,LOW);
  digitalWrite(LED_R,LOW);
  
  }else if(sensor_pressure >= ch0-2 && sensor_pressure <= ch1 && !sensor_low_bound_bool){
  digitalWrite(LED_G,LOW);
  digitalWrite(LED_R,LOW);
  
  }else if(sensor_pressure <= ch1 + 2 && sensor_pressure > ch1 && sensor_high_bound_bool){
  digitalWrite(LED_G,HIGH);
  digitalWrite(LED_R,LOW);
    
  }
  if(sensor_pressure >= ch1){
  sensor_high_bound_bool = 0;
  digitalWrite(LED_G,HIGH);
  digitalWrite(LED_R,HIGH);
    
  }else if(sensor_pressure <= ch1 + 2 && sensor_pressure > ch1 && !sensor_high_bound_bool){
  digitalWrite(LED_G,HIGH);
  digitalWrite(LED_R,HIGH);
    
  }

  
}

int calcPressDisp(){
  pressAvg = 0;
  sensorVal = analogRead(PRESSURE);
    if(sensorVal < 1024/5 * sensorMin){
      pressDisp = 0;
    }
    else if(sensorVal > 1024/5 *sensorMax){
      pressDisp = 1023;
    }
    else{
      pressDisp = map(sensorVal, 1024/5 * sensorMin, 1024/5 *sensorMax, 0, 1023);
    }
    pressArr[circularIdx] = pressDisp;
    circularIdx = (circularIdx + 1) % 5;
    for(int i=0; i<5; i++){
      pressAvg += pressArr[i];
    }
    pressAvg /= 5;
    return pressAvg / 1023 * 100;
}

void pwmOut(){
  pwmOutput = (int) pressAvg/4;
//  analogWrite(PWM_OUTPUT, pwmOutput); //PWM OUTPUT
}

void showPressure(){
  while(!btnState[MD-7]){
    dsp.showNumberDec(calcPressDisp(), true, 3, 1);
    delay(100);
    btnCheck(MD);
    pressCheck();
    pwmOut();
  }
  btnState[MD-7] = false;
}

void setFalse(){
  btnState[0] = false;
  btnState[1] = false;
  btnState[2] = false;
}

void setPressure(){
  delay(TERM);
  while(!btnState[MD-7]){   
    dsp.setSegments(SEG_VAL_L,1,1); 
    dsp.showNumberDec(ch0,true,2,2);
    btnCheck(UP);
    if(btnState[UP-7] && ch0 < 99){
      ch0++;
      delay(INPUT_TERM);
      while(goOn && digitalRead(UP) && ch0 < 99){
        ch0++;
        delay(goOnTERM);
        dsp.showNumberDec(ch0,true,2,2);
      }
      goOn = false;
    }
    btnCheck(DN);
    if(btnState[DN-7] && ch0 > 0){ 
      ch0--;
      delay(INPUT_TERM);
      while(goOn && digitalRead(DN) && ch0 > 0){
        ch0--;
        delay(goOnTERM);
        dsp.showNumberDec(ch0,true,2,2);
      }
      goOn = false;
    }
    btnCheck(MD);
  }
  btnState[MD-7];
  btnCheck(MD);
  while(!btnState[MD-7]){   
    dsp.setSegments(SEG_VAL_H,1,1); 
    dsp.showNumberDec(ch1,true,2,2);
    btnCheck(UP);
    if(btnState[UP-7] && ch0 < 99){
      ch1++;
      delay(INPUT_TERM);
      while(goOn && digitalRead(UP) && ch1 < 99){
        ch1++;
        delay(goOnTERM);
        dsp.showNumberDec(ch1,true,2,2);
      }
      goOn = false;
    }
    btnCheck(DN);
    if(btnState[DN-7] && ch1 > ch0){ 
      ch1--;
      delay(INPUT_TERM);
      while(goOn && digitalRead(DN) && ch1 > ch0){
        ch1--;
        delay(goOnTERM);
        dsp.showNumberDec(ch1,true,2,2);
      }
      goOn = false;
    }
    btnCheck(MD);
  }
  btnState[MD-7] = false;
  dsp.setSegments(SEG_VAL_S,1,1);
  dsp.setSegments(SEG_VAL_A,1,2);
  dsp.setSegments(SEG_VAL_V,1,3);
  EEPROM.put(20, ch0);
  delay(100);
  EEPROM.put(30, ch1);
  delay(900);
}

void setup(){
  pinMode(PRESSURE, INPUT);
  
  pinMode(MD, INPUT);
  pinMode(UP, INPUT);
  pinMode(DN, INPUT);

//  pinMode(PWM_OUTPUT, OUTPUT);

  pinMode(LED_G,OUTPUT);
  pinMode(LED_R,OUTPUT);
  
  dsp.setBrightness(3); // 3
  dsp.showNumberDec(0000);
  Serial.begin(9600);

  for(int i=0; i<5; i++){
    pressArr[i] = analogRead(PRESSURE);
  }
  ch0 = EEPROM.read(20);
  delay(50);
  ch1 = EEPROM.read(30);
  delay(50);
  if(ch0 < 0 || ch0 > 100){
    ch0 = 70;
    ch1 = 80;
  }

  sensorMin = EEPROM.get(0, sensorMin);
  delay(50);
  sensorMax = EEPROM.get(10, sensorMax);
  delay(50);
  if(sensorMin < 0 || sensorMin > 5){
    sensorMin = 2.120;
    sensorMax = 4.250;
  }
  isInit = true;
}

void initiate(){
  for(int i =0; i<5; i++){
    pressArr[i] = map(analogRead(PRESSURE), 1024/5 * sensorMin, 1024/5 *sensorMax, 0, 1023);
    delay(10);
  }
  if(EEPROM.read(50) != 197){
    ch0 = ch0_PREFIX;
    ch1 = ch1_PREFIX;
    EEPROM.put(20, ch0);
    EEPROM.put(30, ch1);
    EEPROM.write(50, 197);
    delay(40);
  }
  isInit = false;
}

void loop() {
  if(isInit){
    initiate();
  }
  showPressure();
  setPressure();
}
