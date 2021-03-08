#include <NewPing.h>
#include<Wire.h>

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
//const short IR1 = 2;
//const short IR2 = 3;
const short MOTOR3 = 3;
const short IN5 = 5;
const short IN6 = 4;
// used for older arduino ide versions
const short LED_BUILDIN = 13;
//const long RPM_FACTOR = 60000; // = 1 minute
//const int MPU=0x68;

//int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;
//long prevCountLeft = 0;
//long prevCountRight = 0;
//unsigned long prevTimeLeft;
//unsigned long prevTimeRight;
//unsigned long prevTime;
boolean obstacleDetected = false;

volatile byte state = LOW;
/*volatile boolean prevLeftVal = LOW;
//volatile boolean prevRightVal = LOW;
volatile long countLeft = 0;
volatile long countRight = 0;
volatile long rpmRight = 0;
volatile long rpmLeft = 0;
volatile short leftEventCount = 0;
volatile short rightEventCount = 0;
*/
byte incoming[4];

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

void setup() {
  //  enable serial
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  //pinMode(IR1, INPUT);
  //pinMode(IR2, INPUT);
  // init interrupts
  //attachInterrupt(digitalPinToInterrupt(IR1), addLeft, FALLING);
  //attachInterrupt(digitalPinToInterrupt(IR2), addRight, FALLING);
  // init mpu
  /*Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); 
  Wire.write(0);    
  Wire.endTransmission(true);*/
  // init moto pins
  pinMode(MOTOR1, OUTPUT);
  pinMode(MOTOR2, OUTPUT);
  pinMode(MOTOR3, OUTPUT); 
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(IN5, OUTPUT);
  pinMode(IN6, OUTPUT);
  //prevTime = millis();
  //prevTimeRight = millis();
}

void loop() {  
  if(Serial.available() >= 4) {
      for (int i = 0; i < 4; i++) {
        incoming[i] = Serial.read();
      }      
  }

  updateData();

  if (obstacleDetected) {
    stopMotors();
  } else {
    runMotors(incoming[0], incoming[1], incoming[2], incoming[3]);
  }

  //sendData();
  //readMpu();  
}

void runMotors(byte leftPower, byte rightPower, byte dir, byte mowerPower) {
  if (dir == 1) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);  
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else if (dir == 2) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);  
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }

  if (mowerPower >= 50) {
    runMower(mowerPower);
  } else if (mowerPower < 50) {
    stopMower();
  } else {
    stopMower();
  }

  analogWrite(MOTOR1, leftPower);
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

void runMower(byte power) {
  digitalWrite(IN5, LOW);
  digitalWrite(IN6, HIGH);
  analogWrite(MOTOR3, power);
}

void stopMower() {
  digitalWrite(IN5, LOW);
  digitalWrite(IN6, LOW);
  analogWrite(MOTOR3, 0);
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

/*long computeRPM(long prevTime, long count, long prevCount, boolean isLeft) {
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
}*/

void updateData() {
  //rpmLeft = computeRPM(prevTimeLeft, countLeft, prevCountLeft, true);
  //rpmRight = computeRPM(prevTimeRight, countRight, prevCountRight, false);

  float distance = sonar.ping_cm();
  if (distance < 10) {
    obstacleDetected = true;
  } else {
    obstacleDetected = false;
  }
}

void sendData() {
  String output = "";
  output.concat(incoming[0]);
  output += ";";
  output.concat(incoming[1]);
  output += ";";
  output.concat(incoming[2]);
  output += ";";
  output.concat(incoming[3]);
  output += ";";
  output.concat(obstacleDetected);
  output += ";";
  Serial.println(output);
 }
