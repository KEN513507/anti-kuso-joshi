const int LED_PIN = 21; // XIAO ESP32S3 内蔵ユーザーLED

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(115200);
  WiFi.onEvent([](arduino_event_id_t event) {
  Serial.printf("EVENT=%d\n", event);
});
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == '1') {
      digitalWrite(LED_PIN, HIGH);
    } else if (c == '0') {
      digitalWrite(LED_PIN, LOW);
    }
  }
}
