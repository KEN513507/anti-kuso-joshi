#include <WiFi.h>
#include "../../secrets/wifi_secrets.h"

// ★ 実際のSSIDとパスワードに書き換えろ！
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

WiFiServer server(80);

void setup() {
  Serial.begin(115200);
  WiFi.onEvent([](arduino_event_id_t event) {
  Serial.printf("EVENT=%d\n", event);
});
  delay(1000);
  Serial.println("\n=== HTTP-ONLY TEST ===");

  // Wi-Fi接続
  Serial.printf("Connecting to %s...\n", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // HTTPサーバー起動
  server.begin();
  Serial.println("HTTP server started on port 80.");
  Serial.println("=== READY ===");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Client connected.");
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: text/plain");
    client.println("Connection: close");
    client.println();
    client.println("XIAO HTTP Test OK!");
    delay(100);
    client.stop();
    Serial.println("Client disconnected.");
  }
}
