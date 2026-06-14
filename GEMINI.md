# Anti-Kuso-Joshi Project: Project Instructions (GEMINI.md)

## Project Overview
XIAO ESP32S3 Senseで取得した映像をUbuntuへ送信し、YOLOv8でローカル推論を実施するデスク監視システム。
**クラウド利用は厳禁。**

## Hardware Context
- **Edge Device**: XIAO ESP32S3 Sense (OV2640 Camera)
- **Host Machine**: Ubuntu 24.04 LTS
- **Network Router**: YAMAHA RTX1200

## Network Configuration
- **Ubuntu Host**: `192.168.100.106`
- **ESP32 Edge**: `192.168.100.101` (STA Mode)
- **Streaming URL**: `http://192.168.100.101` (MJPEG)

## Build & Deployment Rules
- **ESP32 Compile**: 必ず PSRAM を有効化すること。
  - FQBN: `esp32:esp32:XIAO_ESP32S3:PSRAM=opi`
- **PSRAM無効ビルドは禁止。**

## System Architecture
- **ESP32 Side**: 
  - Camera Capture & MJPEG Streaming に専念。
- **Ubuntu Side**:
  - OpenCVによるストリーム取得。
  - YOLOv8によるローカル推論。
  - CSV監査ログの生成。
  - シリアル通信によるESP32 LED通知制御。

## Current Status (Verified)
- [x] Camera Initialization OK (PSRAM=opi)
- [x] WiFi STA Connection OK (192.168.100.101)
- [x] MJPEG Stream over Network OK
- [x] OpenCV Stream Capture & `capture.jpg` Save OK

## Forbidden Actions
- **Cloud AI / External API Usage**: すべての推論はローカルで完結させること。
- **Image Upload**: 外部サーバーへの画像アップロード禁止。
- **Hardcoded Secrets**: SSIDやパスワードの直接記述禁止（`secrets/` を参照）。

## Next Focus: AI Inference & Integration
1. `capture.jpg` に対する YOLOv8 推論の精度検証。
2. 推論結果 (`cup` 判定) に基づく CSV 監査ログの正確な記録。
3. シリアル経由での LED 通知連動の安定化。
