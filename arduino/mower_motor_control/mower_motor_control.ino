#include <NewPing.h>
#include<Wire.h>
#include "SerialTransfer.h"

#define TRIGGER_PIN  6  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     7  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.
#define INPUT_SIZE 7 // Input looks like 200:200

const short MOTOR1 = 10;
const short IN1 = 8;
const short IN2 = 9;
const short MOTOR2 = 11;
const short IN3 = 13;
const short IN4 = 12;
const short IR1 = 2;
const short IR2 = 3;
// used for older arduino ide versions
const short LED_BUILDIN = 13;
const long RPM_FACTOR = 60000; // = 1 minute
//const int MPU=0x68;

int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
long prevCountLeft = 0;
long prevCountRight = 0;
unsigned long prevTimeLeft;
unsigned long prevTimeRight;
unsigned long prevTime;
boolean obstacleDetected = false;

volatile byte state = LOW;
volatile boolean prevLeftVal = LOW;
volatile boolean prevRightVal = LOW;
volatile long countLeft = 0;
volatile long countRight = 0;
volatile long rpmRight = 0;
volatile long rpmLeft = 0;
volatile short leftEventCount = 0;
volatile short rightEventCount = 0;

SerialTransfer transfer;

byte incoming[2];

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

void setup() {
  //  enable serial
  Serial.begin(115200);
  transfer.begin(Serial);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(IR1, INPUT);
  pinMode(IR2, INPUT);
  attachInterrupt(digitalPinToInterrupt(IR1), addLeft, FALLING);
  attachInterrupt(digitalPinToInterrupt(IR2), addRight, FALLING);
  // init mpu
  /*Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);*/
  // put your setup code here, to run once:
  pinMode(MOTOR1, OUTPUT);    
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  prevTime = millis();
  prevTimeRight = millis();
}

void loop() {  
  if(Serial.available() > 0) {
    /*char dataReceived[INPUT_SIZE + 1];
	  byte size = Serial.readBytes(dataReceived, INPUT_SIZE);
    if (size > 1) {
      short left = 0;
      short right = 0;
      // add ending 0
      dataReceived[size] = 0;
      // Read command pair
      char* command = strtok(dataReceived, ":");
      byte count = 0;
      while (command != 0) {
        switch (count) {
          case 0:
            left = atoi(command);
            break;
          case 1:
            right = atoi(command);
            break;
          default:
            count = 0;
            break;
        }
        count++;
        command = strtok(0, ":");
      }*/

     
      for (int i = 0; i < 2; i++) {
        incoming[i] = Serial.read();
      }
  
      runMotors(incoming[0], incoming[1]);
  }

  if ((millis() - prevTime) >= 500) {
    updateData();
    prevTime = millis();
  }

  if (obstacleDetected) {
      stopMotors();
  }
       
  //readMpu();  
}

void runMotors(byte leftPower, byte rightPower) {
  Serial.print("Left: ");
  Serial.print(leftPower);
  Serial.print(" Right: ");
  Serial.println(rightPower);
  digitalWrite(IN1, HIGH);  // Motor 1 beginnt zu rotieren
  digitalWrite(IN2, LOW);
  analogWrite(MOTOR1, leftPower);

  digitalWrite(IN3, HIGH);  // Motor 2 beginnt zu rotieren
  digitalWrite(IN4, LOW);
  analogWrite(MOTOR2, rightPower);
}

void stopMotors() {  
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(MOTOR1, 0);
  analogWrite(MOTOR2, 0);  
}

/*void readMpu() {
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  
  Wire.endTransmission(false);
  Wire.requestFrom(MPU,12,true);  
  AcX=Wire.read()<<8|Wire.read();    
  AcY=Wire.read()<<8|Wire.read();  
  AcZ=Wire.read()<<8|Wire.read();  
  GyX=Wire.read()<<8|Wire.read();  
  GyY=Wire.read()<<8|Wire.read();  
  GyZ=Wire.read()<<8|Wire.read();  
  
  Serial.print("Accelerometer: ");
  Serial.print("X = "); Serial.print(AcX);
  Serial.print(" | Y = "); Serial.print(AcY);
  Serial.print(" | Z = "); Serial.println(AcZ); 
  
  Serial.print("Gyroscope: ");
  Serial.print("X = "); Serial.print(GyX);
  Serial.print(" | Y = "); Serial.print(GyY);
  Serial.print(" | Z = "); Serial.println(GyZ);
  Serial.println(" ");
  delay(333);
}*/

long computeRPM(long prevTime, long count, long prevCount, boolean isLeft) {
  double t = millis() - prevTime;
  long rpm = 0;
  long tempCount = count - prevCount;
  
  rpm = (tempCount/t) * RPM_FACTOR;
  
  if (isLeft) {
    prevTimeLeft = t;
    prevCountLeft = count;
  } else {
    prevTimeRight = t;
    prevCountRight = count;
  }
  return rpm;
}

void addLeft() {
  leftEventCount++;
  // the ir sensor fires 4 times, so only the 4th times counts
  if (leftEventCount == 5) {
    addCount(true, prevTimeLeft);
    leftEventCount = 0;
  }
}

void addRight() {
  rightEventCount++;
  // the ir sensor fires 4 times, so only the 4th times counts
  if (rightEventCount == 5) {
    addCount(false, prevTimeRight);
    rightEventCount = 0;
  }
  
}

void addCount(boolean isLeft, long prevTime) {
  int timeDiv = millis() - prevTime;
  if (timeDiv > 600) {
    if (isLeft) {
      countLeft = countLeft + 1;
      prevTimeLeft = millis();
    } else {
      countRight = countRight + 1;
      prevTimeRight = millis();
    }
  }
}

void updateData() {
  rpmLeft = computeRPM(prevTimeLeft, countLeft, prevCountLeft, true);
  rpmRight = computeRPM(prevTimeRight, countRight, prevCountRight, false);

  float distance = sonar.ping_cm();
  if (distance < 10) {
    obstacleDetected = true;
  } else {
    obstacleDetected = false;
  }

  sendData();
}

void sendData() {
  String output = "";
  output.concat(countLeft);
  output += ";";
  output.concat(rpmLeft);
  output += ";";
  output.concat(countRight);
  output += ";";
  output.concat(rpmRight);
  output += ";";
  output.concat(obstacleDetected);
  output += ";";
  //Serial.print(output);
 }
