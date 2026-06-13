#!/usr/bin/env python3
"""
Anti-Kuso-Joshi Project: 自己主権型デスク監視システム
要件定義書 docs/requirements.md に基づく実装
"""

import cv2
from ultralytics import YOLO
import serial
import time
import os
import sys
import signal

============================================
定数定義 (マジックナンバー撲滅)
============================================
STREAM_URL = "http://192.168.100.101" # XIAO S3 SenseのIPアドレス
CUP_CLASS_ID = 41
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
CAMERA_TIMEOUT = 1.5 # NFR-03: タイムアウトリトライ

============================================
# # NFR-04: ゾンビプロセスキラー
============================================
def kill_zombie_processes():
"""カメラを掴んでいる可能性のある全てのPythonプロセスを掃討する"""
print("[SYSTEM] ゾンビプロセス一掃作戦を開始します...")
os.system('pkill -9 -f fall_detect.py 2>/dev/null')
os.system('pkill -9 -f cup_detector.py 2>/dev/null')
os.system('pkill -9 -f xiao_cup_detector.py 2>/dev/null')
time.sleep(0.5)

def signal_handler(sig, frame):
print("\n[SYSTEM] 強制終了シグナルを受信。システムを安全に停止します。")
sys.exit(0)

============================================
メイン処理
============================================
def main():

シグナルハンドラ設定
signal.signal(signal.SIGINT, signal_handler)

起動時のクリーンアップ
kill_zombie_processes()

AIモデルロード
print("[AI] YOLOv8n をローカルにロードしています...")
model = YOLO("yolov8n.pt")

シリアル通信初期化
led_ser = None
try:
led_ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
print(f"[I/O] ESP32 LED制御ポート {SERIAL_PORT} を確保しました。")
except:
print("[I/O] LEDデバイスが未接続です。画面表示のみ継続します。")

映像ストリームキャプチャ
print(f"[VISION] エッジデバイス {STREAM_URL} に接続しています...")
cap = cv2.VideoCapture(STREAM_URL)
if not cap.isOpened():
print("[ERROR] 映像ストリームを開けません。XIAO S3のIPアドレスと電源を確認してください。")
sys.exit(1)

print("[SYSTEM] 自己主権型監視システムが起動しました。Ctrl+Cで終了。")

while True:
ret, frame = cap.read()
if not ret:
print(f"[WARNING] フレーム取得失敗。{CAMERA_TIMEOUT}秒後にリトライします...")
time.sleep(CAMERA_TIMEOUT)
continue

results = model(frame, verbose=False)
cup_found = False

for box in results[0].boxes:
if int(box.cls[0]) == CUP_CLASS_ID:
x1, y1, x2, y2 = map(int, box.xyxy[0])
cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 3)
cv2.putText(frame, "☕ CUP LOCKED", (x1, y1-10),
cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
cup_found = True
break

HUD表示
if cup_found:
cv2.putText(frame, "STATUS: ENGAGED", (10, 30),
cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
cv2.putText(frame, "WARNING: Boss incoming?", (10, 70),
cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)
if led_ser: led_ser.write(b'1')
else:
cv2.putText(frame, "STATUS: DISENGAGED", (10, 30),
cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)
if led_ser: led_ser.write(b'0')

cv2.imshow("Anti-Kuso-Joshi // Sovereign AI Monitor", frame)
if cv2.waitKey(1) & 0xFF == ord('q'):
break

cap.release()
cv2.destroyAllWindows()
if led_ser: led_ser.close()

if name == "main":
main()
