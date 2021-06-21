const short MOTOR1 = 10;
const short IN1 = 8;
const short IN2 = 9;
const short MOTOR2 = 11;
const short IN3 = 13;
const short IN4 = 12;
const short MOTOR3 = 5;
// used for older arduino ide versions
const short LED_BUILDIN = 13;
byte incoming[4];

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

  runMotors(incoming[0], incoming[1], incoming[2], incoming[3]);
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

  if (mowerPower >= 129) {
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
  stopMower();
}

void runMower() {
  digitalWrite(MOTOR3, HIGH);
}

void stopMower() {
  digitalWrite(MOTOR3, LOW);
}
