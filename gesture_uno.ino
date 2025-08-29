#define IR_SENSOR_PIN 2
#define BUZZER_PIN 8
#define LED_PIN 13
#define TRIG_PIN 9
#define ECHO_PIN 10

long duration;
int distance;
bool gestureDetected = false;

void setup() {
  pinMode(IR_SENSOR_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  Serial.begin(9600);
}

void loop() {
  // IR SENSOR check (hand too close)
  if (digitalRead(IR_SENSOR_PIN) == LOW) {
    digitalWrite(BUZZER_PIN, HIGH);  // Hand too close
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }

  // Ultrasonic Sensor: check if hand is too far
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  if (distance > 30) {
    digitalWrite(LED_PIN, HIGH);  // Too far, turn on light
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  // Handle gesture blink signal from Python
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'B') {
      digitalWrite(LED_PIN, HIGH);
      delay(100);
      digitalWrite(LED_PIN, LOW);
    }
  }

  delay(100);
}
