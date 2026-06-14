# Anti-Kuso-Joshi Project: Current Status & System Architecture

## 1. 動作確定済みステータス (Verified)
以下の項目は検証済みであり、再検証不要な「既知の事実」として定義する。

- **Hardware**: XIAO ESP32S3 Sense + OV2640
- **Compile**: FQBN `esp32:esp32:XIAO_ESP32S3:PSRAM=opi` (PSRAM必須)
- **Network**:
  - ESP32 (STA Mode): `192.168.100.101`
  - Ubuntu (Host): `192.168.100.106`
  - Router: YAMAHA RTX1200
- **Streaming**: MJPEG Stream (`http://192.168.100.101`)
- **Capture**: OpenCVによるストリーム取得および `capture.jpg` の保存成功。
- **Inference**: Ubuntu 24.04上での YOLOv8 (ultralytics) ローカル推論の動作。

## 2. システムアーキテクチャ
### Edge Side (ESP32)
- **Role**: 映像配信専用機。
- **Primary Task**: OV2640からのキャプチャおよびHTTP MJPEGストリーミング。
- **Secondary Task**: Ubuntuからのシリアル指示によるLED（Yellow）制御。

### Host Side (Ubuntu 24.04)
- **Role**: 司令塔・推論エンジン。
- **Inference**: YOLOv8によるローカル物体検出（クラウド利用禁止）。
- **Data Integrity**: CSV監査ログによる検知履歴の保存。
- **Control**: 検知結果に基づき、USBシリアル経由でESP32へ通知。

## 3. 開発フェーズの遷移
- **Phase 1: Connectivity (DONE)**: Wi-Fi接続、ストリーミング、映像保存の確立。
- **Phase 2: Intelligence & Integration (ACTIVE)**:
  - YOLO推論の精度向上（cup判定）。
  - 判定結果と監査ログ（CSV）の連携。
  - 推論結果に連動したリアルタイムLED通知。

## 4. 禁止事項 (Immutable Rules)
- クラウドAI（API）の利用禁止。
- 外部への画像アップロード禁止。
- PSRAM無効状態でのビルド禁止。
