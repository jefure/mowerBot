#include <NewPing.h>
#include<Wire.h>

#define TRIGGER_PIN  6  // Arduino pin tied to trigger pin on the ultrasonic sensor.
#define ECHO_PIN     7  // Arduino pin tied to echo pin on the ultrasonic sensor.
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters). Maximum sensor distance is rated at 400-500cm.

const short MOTOR = 10;
const short IN1 = 9;
const short IN2 = 8;
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

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

void setup() {
  //  enable serial
  Serial.begin(115200);
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
  pinMode(MOTOR, OUTPUT);    
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  prevTime = millis();
  prevTimeRight = millis();
}

void loop() {  
  int dataReceived = -1;
  if(Serial.available() > 0) {
	  dataReceived = Serial.read();

    if (dataReceived == '1') {
      runMotor(255);
      digitalWrite( LED_BUILDIN, HIGH);
    } else if (dataReceived == '0') {
       stopMotor();
       digitalWrite( LED_BUILDIN, LOW);
    } else if (dataReceived == '3') {
       digitalWrite( LED_BUILDIN, HIGH);
    }
  }

  if ((millis() - prevTime) >= 1000) {
    updateData();
    prevTime = millis();
  }
       
  // put your main code here, to run repeatedly:
  //readMpu();  
}

void runMotor(int power) {
  digitalWrite(IN1, LOW);  // Motor 1 beginnt zu rotieren
  digitalWrite(IN2, HIGH);
  analogWrite(MOTOR, power);
}

void stopMotor() {
  digitalWrite(IN1, HIGH);  
  digitalWrite(IN2, LOW);
  analogWrite(MOTOR, 200);
  delay(500);
  
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
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
  Serial.print(output);
 }
