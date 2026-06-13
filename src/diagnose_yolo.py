#!/usr/bin/env python3
"""YOLO沈黙破り診断: 全ての検出物をリストアップし、画像を保存する"""

import cv2
from ultralytics import YOLO
import numpy as np

STREAM_URL = "http://192.168.100.101"
CONF_THRESHOLD = 0.05  # 極限まで下げて、どんな候補も拾う

def main():
    print(f"[診断] XIAO ストリーム {STREAM_URL} に接続します...")
    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        print("❌ 接続失敗。IPアドレスと電源を確認せよ。")
        return

    model = YOLO("yolov8n.pt")
    print(f"[診断] モデル読み込み完了。クラス一覧 (model.names):")
    print(model.names)

    # 安定するまで数フレーム読み飛ばす
    for _ in range(10):
        cap.read()

    success, frame = cap.read()
    cap.release()

    if not success:
        print("❌ フレーム取得失敗。")
        return

    # 画像を保存 (証拠)
    cv2.imwrite("evidence_diagnostic.jpg", frame)
    print("[診断] 画像を 'evidence_diagnostic.jpg' に保存しました。")

    # YOLO 推論 (超低閾値)
    results = model(frame, conf=CONF_THRESHOLD, verbose=False)

    if results and len(results) > 0 and results[0].boxes is not None:
        print(f"[診断] 検出された物体数: {len(results[0].boxes)}")
        for box in results[0].boxes:
            cls = int(box.cls)
            conf = float(box.conf)
            name = model.names[cls] if cls in model.names else "unknown"
            print(f"  class={cls} name={name} conf={conf:.2f}")
    else:
        print("[診断] ⚠️ 何も検出されませんでした (閾値0.05でもゼロ)。")
        print("  可能性: カメラが真っ暗、レンズキャップ、物体が小さすぎる、など。")

    print("[診断] 完了。'evidence_diagnostic.jpg' を目視で確認し、上記のクラス一覧と照合せよ。")

if __name__ == "__main__":
    main()
