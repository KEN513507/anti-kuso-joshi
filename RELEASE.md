# Anti-Kuso-Joshi Project リリースノート

## 実証された機能
- YOLOv8n による CPU 推論（平均 0.073 秒、約 13.6 FPS）
- `cup` (conf=0.57)、`bottle` (conf=0.36) の物体検出
- CSV 監査ログと混合行列による定量評価基盤
- ESP32 シリアル通信と LED 制御
- XIAO ESP32S3 の Wi-Fi AP モード HTTP サーバー

## 未解決の課題
- 特になし (XIAO カメラ初期化問題は解決)

## 修正履歴
### 2026-06-13
- **原因:** Arduino CLIのPSRAM設定が無効であったため、カメラバッファの確保に失敗していた。
- **修正:** コンパイル時に `--fqbn "esp32:esp32:XIAO_ESP32S3:PSRAM=opi"` を指定することで解決。
- **結果:** `PSRAM=1` となり、`esp_camera_init()` が成功。OV2640 正常動作を確認。

## 次の一手
1. XIAO を STA モードへ移行し、既存ネットワーク内でのストリーミングを安定化させる。
2. OpenCV による映像取得の検証。
