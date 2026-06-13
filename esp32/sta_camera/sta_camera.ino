#include "esp_camera.h"
#include <WiFi.h>
#include "../../secrets/wifi_secrets.h"
// ★ 既存のWi-Fi設定
 const char* ssid = WIFI_SSID;
 const char* password = WIFI_PASSWORD;


// XIAO ESP32S3 内蔵LED (Yellow)
#define LED_PIN 21

// カメラピン定義 (XIAO ESP32S3 Sense)
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     10
#define SIOD_GPIO_NUM     40
#define SIOC_GPIO_NUM     39
#define Y9_GPIO_NUM       48
#define Y8_GPIO_NUM       11
#define Y7_GPIO_NUM       12
#define Y6_GPIO_NUM       14
#define Y5_GPIO_NUM       16
#define Y4_GPIO_NUM       18
#define Y3_GPIO_NUM       17
#define Y2_GPIO_NUM       15
#define VSYNC_GPIO_NUM    38
#define HREF_GPIO_NUM     47
#define PCLK_GPIO_NUM     13

WiFiServer server(80);

void setup() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH); // LED OFF (Active LOW)

  Serial.begin(115200);
  delay(3000); // 起動待ち
  Serial.println("\n\n=== XIAO STA MODE ===");

  if(psramFound()){
    Serial.println("PSRAM: Found (OK)");
  } else {
    Serial.println("PSRAM: NOT FOUND (ERROR)");
  }

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;

  Serial.print("Camera init... ");
  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("FAILED!");
    while(1) { // 失敗時：点滅
      digitalWrite(LED_PIN, LOW); delay(100);
      digitalWrite(LED_PIN, HIGH); delay(100);
    }
  }
  Serial.println("OK");

  // Wi-Fi設定のリセット
  Serial.println("WiFi Resetting...");
  Serial.print("MAC=");
  Serial.println(WiFi.macAddress());
  WiFi.mode(WIFI_STA);
 WiFi.mode(WIFI_STA);

  WiFi.disconnect(true, true);
  delay(3000);

  Serial.println("START CONNECT");

  WiFi.begin(ssid, password);

  // 周辺ネットワークのスキャン
  Serial.println("SCAN START");
  int n = WiFi.scanNetworks();
  Serial.printf("FOUND=%d\n", n);
  if (n > 0) {
    Serial.printf(
      "TARGET_CANDIDATE: SSID=%s RSSI=%d CH=%d\n",
      WiFi.SSID(0).c_str(),
      WiFi.RSSI(0),
      WiFi.channel(0)
    );
  }
  for (int i = 0; i < n; i++) {
    Serial.printf(
      "%d: %s RSSI=%d CH=%d\n",
      i,
      WiFi.SSID(i).c_str(),
      WiFi.RSSI(i),
      WiFi.channel(i)
    );
  }

  // Wi-Fi接続
  Serial.printf("Connecting to %s... ", ssid);
  WiFi.begin(ssid, password);

  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 30) {
    delay(500);
    Serial.print(".");
    Serial.print(" retry=");
    Serial.print(retry);
    Serial.print(" status=");
    Serial.println(WiFi.status());
    digitalWrite(LED_PIN, !digitalRead(LED_PIN)); // Wi-Fi接続中：ゆっくり点滅
    retry++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(LED_PIN, LOW); // 成功：LED常時点灯
  } else {
    Serial.println("\nWiFi Failed!");
    digitalWrite(LED_PIN, HIGH); // 失敗：LED消灯
  }

  server.begin();
  Serial.println("HTTP Server Started.");
  Serial.println("=== READY ===");
}

void loop() {
  static unsigned long last_log = 0;
  if (millis() - last_log > 5000) {
    last_log = millis();
    Serial.printf("RUNNING | WiFi=%d | RSSI=%d\n", WiFi.status(), WiFi.RSSI());
  }

  WiFiClient client = server.available();
  if (client) {
    Serial.println("CLIENT CONNECTED");
    String currentLine = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n') {
          if (currentLine.length() == 0) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
            client.println();
            while (client.connected()) {
              camera_fb_t * fb = esp_camera_fb_get();
              if (!fb) { delay(1); continue; }
              client.println("--frame");
              client.println("Content-Type: image/jpeg");
              client.print("Content-Length: ");
              client.println(fb->len);
              client.println();
              client.write(fb->buf, fb->len);
              client.println();
              esp_camera_fb_return(fb);
              delay(50);
            }
            break;
          } else {
            currentLine = "";
          }
        } else if (c != '\r') {
          currentLine += c;
        }
      }
    }
    client.stop();
  }
}
