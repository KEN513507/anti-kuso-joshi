void setup() {
  pinMode(21, OUTPUT); // XIAO ESP32S3 内蔵ユーザーLED
}
void loop() {
  digitalWrite(21, HIGH);
  delay(500);
  digitalWrite(21, LOW);
  delay(500);
}
