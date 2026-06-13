# Anti-Kuso-Joshi Project リリースノート

## 実証された機能
- YOLOv8n による CPU 推論（平均 0.073 秒、約 13.6 FPS）
- `cup` (conf=0.57)、`bottle` (conf=0.36) の物体検出
- CSV 監査ログと混合行列による定量評価基盤
- ESP32 シリアル通信と LED 制御
- XIAO ESP32S3 の Wi-Fi AP モード HTTP サーバー

## 未解決の課題
- XIAO の OV2640 カメラモジュールが `esp_camera_init()` でエラー (0xffffffff)
- フラットケーブル再接続、PSRAM 設定変更でも改善せず
- 結論: カメラモジュールの物理的故障の可能性が高い

## 次の一手
1. XIAO のカメラモジュールを交換する (Seeed Studio で別途購入可能)
2. USB カメラでの再構築（UVC ドライバーの安定性に注意）
