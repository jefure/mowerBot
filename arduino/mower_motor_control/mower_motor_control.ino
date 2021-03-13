#include <NewPing.h>

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
const short MOTOR3 = A0;
// used for older arduino ide versions
const short LED_BUILDIN = 13;
boolean obstacleDetected = false;
byte incoming[4];

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.

void setup() {
  //  enable serial
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  // init moto pins
  pinMode(MOTOR1, OUTPUT);
  pinMode(MOTOR2, OUTPUT);
  pinMode(MOTOR3, OUTPUT); 
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void loop() {  
  if(Serial.available() >= 4) {
      for (int i = 0; i < 4; i++) {
        incoming[i] = Serial.read();
      }      
  }

  //updateData();

  if (obstacleDetected) {
    stopMotors();
  } else {
    runMotors(incoming[0], incoming[1], incoming[2], incoming[3]);
  }

  //sendData();
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

  if (mowerPower == 129) {
    runMower();
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

void runMower() {
  digitalWrite(MOTOR3, HIGH);
}

void stopMower() {
  digitalWrite(MOTOR3, LOW);
}


void updateData() {
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
