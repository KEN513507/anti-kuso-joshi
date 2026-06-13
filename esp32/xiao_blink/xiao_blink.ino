void setup() {
  Serial.begin(115200);
  WiFi.onEvent([](arduino_event_id_t event) {
  Serial.printf("EVENT=%d\n", event);
});
  while(!Serial); // Wait for Serial to be ready
  Serial.println("XIAO ESP32S3 Serial Test Start");
  pinMode(21, OUTPUT); // XIAO ESP32S3 内蔵ユーザーLED (Yellow)
}

void loop() {
  Serial.println("Blinking...");
  digitalWrite(21, HIGH);
  delay(1000);
  digitalWrite(21, LOW);
  delay(1000);
}
