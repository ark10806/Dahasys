/**
 * 0630 LSC PSC 키 변경
 */
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
#define ch0_PREFIX 60
//###############################################################


//##################################################################################
#define SERIAL_TERM 100
//##################################################################################
float sensorMin = 2.420;
float sensorMax = 4.250;
int hysteresis_value = 2;
//==================================================================================
 bool display_onoff = 1;                                    // display show 
//==================================================================================
float MIN = 2.120;
TM1637Display dsp(CLK, DIO);

int ch0;
const uint8_t SEG_VAL_D[] = {SEG_B | SEG_C | SEG_D | SEG_E | SEG_G}; // d
const uint8_t SEG_VAL_S[] = {SEG_A | SEG_F | SEG_G | SEG_C | SEG_D};
const uint8_t SEG_VAL_A[] = {SEG_A | SEG_F | SEG_B | SEG_G | SEG_E | SEG_C};
const uint8_t SEG_VAL_V[] = {SEG_F | SEG_B | SEG_E | SEG_C | SEG_D};

const uint8_t SEG_VAL_P[] = {SEG_A | SEG_F | SEG_E | SEG_G | SEG_B};
const uint8_t SEG_VAL_C[] = {SEG_A | SEG_F | SEG_E | SEG_D};
const uint8_t SEG_VAL_L[] = {SEG_F | SEG_E | SEG_D};

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
bool isInit;
long startTime;
long startTime2;
long startTime3;
long VsetTime = 5000;
int sav_term = 70;

void setPrefix(){
  sensorMin = (float)analogRead(PRESSURE)/1024*5;
  EEPROM.put(0, sensorMin);
  delay(sav_term);
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
  EEPROM.put(10, sensorMax);
  delay(2000);
  blinkDP(500);
  blinkDP(500);
  btnState[MD-7] = false;
  while(millis() - startTime < 5000){
    if(!digitalRead(MD))  return;
  }
  int term_init_save = 70;
  blinkDP(term_init_save);
  EEPROM.put(70, sensorMin);
  delay(sav_term);
  EEPROM.put(80, sensorMax);
  delay(sav_term);
  for(int i=0; i<5; i++){
    blinkDP(term_init_save);
  }
}

void blinkDP(int term){
  digitalWrite(LED_G, HIGH);
//  dsp.setBrightness(0);
  delay(term);
  digitalWrite(LED_G, LOW);
//  dsp.setBrightness(3);
  delay(term);
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
      //need to signal on disp
      blinkDP(500);
//      delay(1000);
//      startTime = millis();
//      while(millis() - startTime < VsetTime){
//        if(!digitalRead(DN))
//          return;
//      }
      /*
       1. Re-Calibration (LSC - PSC)
            MD 5sec
            점멸 1초 내로 DN
            점멸 0.5초 내로 UP
            점멸 0.5초 내로 DN
            
       2. Setting Initial Calibration
            PSC 값 맞춘 상태에서 MD 7초간 누름
            -> 완료시 5번 점멸
            
       3. Restore to last Calibration
            MD 5sec
            점멸 1초 내로 UP 15초간 누름
            -> 완료시 15번 빠르게 점멸
            
       */
      startTime = millis();
      while(millis() - startTime < 1000){
        if(digitalRead(DN)){
          blinkDP(500);
          startTime2 = millis();
          while(millis() - startTime2 < 1000){
            if(digitalRead(UP)){
              blinkDP(500);
              startTime3 = millis();
              while(millis() - startTime3 < 1000){
                if(digitalRead(DN)) break;
                else if(digitalRead(MD)) return;
              }
            }
            else if(digitalRead(MD)) return;
          }
        }
        else if(digitalRead(UP)){ //깜빡인 후 Up 버튼을 5초간 누르면 초기화
          startTime = millis();
          while(millis() - startTime < 5000){
            if(!digitalRead(UP))  return;
          }
          blinkDP(70);
          sensorMin = EEPROM.get(70, sensorMin);
          delay(sav_term);
          blinkDP(70);
          blinkDP(70);
          sensorMax = EEPROM.get(80, sensorMax);
          delay(sav_term);
          blinkDP(70);
          blinkDP(70);
          blinkDP(70);
          btnState[btnIdx] = false;
          return;
        }
        else return;
      }
      //#######################
      btnState[btnIdx] = false;      
      setPrefix();
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
  float desired_pressure = (float)ch0 / 100 * 1023;
  float sensor_pressure_avg = pressAvg;
  if(control_hysteresis_bool){ //voltage comparison
    if(desired_pressure > sensor_pressure_avg){
      //digitalWrite(PWM_OUTPUT,NORMAL);
      digitalWrite(LED_R, NORMAL);
      
    }else if(desired_pressure >= sensor_pressure_avg && desired_pressure - 8 * hysteresis_value < sensor_pressure_avg){
      //digitalWrite(PWM_OUTPUT,ABNORMAL);
      digitalWrite(LED_R, ABNORMAL);
      
    }else{
     // digitalWrite(PWM_OUTPUT,ABNORMAL);
      digitalWrite(LED_R, ABNORMAL);
      control_hysteresis_bool = 0;
     }
  }else{
    if(desired_pressure - 8 * hysteresis_value < sensor_pressure_avg){
     // digitalWrite(PWM_OUTPUT,ABNORMAL);
      digitalWrite(LED_R, ABNORMAL);
     }else{
//      digitalWrite(PWM_OUTPUT,NORMAL);
      digitalWrite(LED_R, NORMAL);
      control_hysteresis_bool = 1;

      }
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

void setPressure(){
  dsp.setSegments(SEG_VAL_D,1,1);
  delay(TERM);
  while(!btnState[MD-7]){    
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
  btnState[MD-7] = false;
  dsp.setSegments(SEG_VAL_S,1,1);
  dsp.setSegments(SEG_VAL_A,1,2);
  dsp.setSegments(SEG_VAL_V,1,3);
  EEPROM.put(20, ch0);
  delay(1000);
}

void initiate(){
  for(int i =0; i<5; i++){
    pressArr[i] = map(analogRead(PRESSURE), 1024/5 * sensorMin, 1024/5 *sensorMax, 0, 1023);
    delay(10);
  }
  if(EEPROM.read(50) != 196){
    ch0 = ch0_PREFIX;
    EEPROM.put(20, ch0);
    delay(sav_term);
    EEPROM.write(50, 196);
    delay(40);
  }
  isInit = false;
}

void setup(){
  pinMode(PRESSURE, INPUT);
  
  pinMode(MD, INPUT);
  pinMode(UP, INPUT);
  pinMode(DN, INPUT);

  //pinMode(PWM_OUTPUT, OUTPUT);
  
  pinMode(LED_G, OUTPUT);
  pinMode(LED_R, OUTPUT);
  
  dsp.setBrightness(3); // 3
  dsp.showNumberDec(0000);
  Serial.begin(9600);

  ch0 = EEPROM.get(20, ch0);
  delay(sav_term);
  if(ch0 < 0 || ch0 > 100){
    ch0 = 70;
  }

  sensorMin = EEPROM.get(0, sensorMin);
  delay(sav_term);
  sensorMax = EEPROM.get(10, sensorMax);
  delay(sav_term);
  if(sensorMin < 0 || sensorMin > 5){
    sensorMin = 2.120;
    sensorMax = 4.250;
  }
  isInit = true;
}

void loop() {
  if(isInit){
    initiate();
  }
  showPressure();
  setPressure();
}
