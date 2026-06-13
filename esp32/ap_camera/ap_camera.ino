#include "esp_camera.h"
#include <WiFi.h>
#include "../../secrets/wifi_secrets.h"

// ★ XIAOが作るWi-Fiネットワークの名前とパスワード
const char* ap_ssid = "XIAO_CAM";
const char* ap_password = "12345678";

// カメラピン定義
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
  Serial.begin(115200);
  WiFi.onEvent([](arduino_event_id_t event) {
  Serial.printf("EVENT=%d\n", event);
});
  delay(2000);
  Serial.println("\n=== XIAO AP MODE ===");

  // カメラ初期化
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
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

  Serial.print("[1/2] Camera init... ");
  Serial.printf("PSRAM=%u\n", psramFound());
  esp_err_t err = esp_camera_init(&config);

  if (err != ESP_OK) {
    Serial.printf("FAILED! err=0x%x\n", err);
    Serial.printf("PSRAM=%u\n", psramFound());
    return;
  }
  Serial.println("OK");

  // アクセスポイント起動
  Serial.print("[2/2] Starting AP... ");
  WiFi.softAP(ap_ssid, ap_password);
  Serial.println("OK");
  Serial.print("SSID: ");
  Serial.println(ap_ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.softAPIP());

  server.begin();
  Serial.println("HTTP server started.");
  Serial.println("=== READY ===");
}

void loop() {
  WiFiClient client = server.available();
  if (client) {
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
              if (!fb) { delay(10); continue; }
              client.println("--frame");
              client.println("Content-Type: image/jpeg");
              client.print("Content-Length: ");
              client.println(fb->len);
              client.println();
              client.write(fb->buf, fb->len);
              client.println();
              esp_camera_fb_return(fb);
              delay(10);
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
