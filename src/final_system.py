#!/usr/bin/env python3
"""
Anti-Kuso-Joshi Project: 最終リアルタイム検知システム (修正版)
- フレームスキップと混合行列集計の不整合を修正
- last_ai_detected による安定した状態保持
"""

import cv2
import time
import csv
import os
import serial
from datetime import datetime
from ultralytics import YOLO

STREAM_URL = "http://192.168.100.101"
CUP_CLASS_ID = 41
BOTTLE_CLASS_ID = 39
CONF_THRESHOLD = 0.25  # 0.57 の実績を踏まえた実用的な閾値
INFER_SIZE = (320, 240)
FRAME_SKIP = 3
LOG_DIR = "evidence_logs"
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200

def main():
    print(f"【最終システム起動】XIAOストリーム ({STREAM_URL})")

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(LOG_DIR, f"final_evidence_{timestamp}.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "GroundTruth", "AIDetected", "InferTime", "Confidence"])

    print(f"📁 監査ログ: {csv_path}")

    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        print("❌ XIAOに接続できません。")
        return

    model = YOLO("yolov8n.pt")

    led_ser = None
    try:
        led_ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print(f"✅ ESP32 LED制御ポート {SERIAL_PORT} を確保しました。")
    except:
        print("⚠️ LEDデバイスが未接続です。画面表示のみ継続します。")

    tp, fp, tn, fn = 0, 0, 0, 0
    infer_times = []
    current_ground_truth = False
    frame_count = 0
    last_ai_detected = False   # ★ 前回の検出結果を保持
    last_confidence = 0.0

    print("\n📊 リアルタイム検知システム稼働中...")
    print("    t : コップあり / f : コップなし / q : 終了")
    print("-" * 50)

    import threading
    user_command = []
    def get_input():
        while True:
            cmd = input()
            user_command.append(cmd)
            if cmd == 'q':
                break
    input_thread = threading.Thread(target=get_input, daemon=True)
    input_thread.start()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            time.sleep(0.1)
            continue

        if user_command:
            cmd = user_command.pop(0).strip().lower()
            if cmd == 't':
                current_ground_truth = True
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🟢 Ground Truth: CUP PRESENT")
            elif cmd == 'f':
                current_ground_truth = False
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔴 Ground Truth: CUP ABSENT")
            elif cmd == 'q':
                print("終了指示を受け付けました。")
                break

        frame_count += 1
        infer_sec = 0.0

        # ★ 推論はスキップ間隔でのみ実行
        if frame_count % FRAME_SKIP == 0:
            infer_frame = cv2.resize(frame, INFER_SIZE)
            t0 = time.time()
            results = model(infer_frame, conf=CONF_THRESHOLD, verbose=False)
            infer_sec = time.time() - t0
            infer_times.append(infer_sec)

            # 検出結果を更新
            detected = False
            max_conf = 0.0
            try:
                if results and len(results) > 0 and results[0].boxes is not None:
                    for box in results[0].boxes:
                        cls = int(box.cls)
                        conf = float(box.conf)
                        if cls == CUP_CLASS_ID or cls == BOTTLE_CLASS_ID:
                            xyxy = box.xyxy.cpu().numpy().flatten()
                            scale_x = frame.shape[1] / INFER_SIZE[0]
                            scale_y = frame.shape[0] / INFER_SIZE[1]
                            x1 = int(xyxy[0] * scale_x)
                            y1 = int(xyxy[1] * scale_y)
                            x2 = int(xyxy[2] * scale_x)
                            y2 = int(xyxy[3] * scale_y)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                            label = f"{model.names[cls]} {conf:.2f}"
                            cv2.putText(frame, label, (x1, y1-10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                            detected = True
                            max_conf = max(max_conf, conf)
            except Exception as e:
                pass

            last_ai_detected = detected
            last_confidence = max_conf

            # ★ 混合行列の集計はここでのみ行う（偽FNの発生を防ぐ）
            if current_ground_truth and detected:
                tp += 1
            elif not current_ground_truth and detected:
                fp += 1
            elif not current_ground_truth and not detected:
                tn += 1
            elif current_ground_truth and not detected:
                fn += 1

        # 全フレームでCSVログとLED制御を実施（前回の検出結果を使用）
        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), current_ground_truth, last_ai_detected, f"{infer_sec:.3f}", f"{last_confidence:.2f}"])

        if led_ser:
            led_ser.write(b'1' if last_ai_detected else b'0')

        # GUI表示
        avg_infer = sum(infer_times) / len(infer_times) if infer_times else 0
        status_color = (0, 255, 0) if last_ai_detected else (0, 0, 255)
        gt_str = "CUP PRESENT" if current_ground_truth else "CUP ABSENT"

        cv2.putText(frame, f"YOLO: {infer_sec:.3f}s (avg: {avg_infer:.3f}s)", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"GT: {gt_str}", (10, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"DETECT: {'YES' if last_ai_detected else 'NO'}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
        cv2.putText(frame, f"TP:{tp} FP:{fp} TN:{tn} FN:{fn}", (10, 95),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.imshow("Anti-Kuso-Joshi // FINAL SYSTEM", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if led_ser: led_ser.close()

    total = tp + fp + tn + fn
    print("\n" + "="*50)
    print("📊 最終リアルタイム検知システム レポート (修正版)")
    print("="*50)
    print(f" 総サンプル数: {total}")
    print(f" TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}")
    print("-"*50)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / total if total > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f" Precision: {precision*100:.1f}%")
    print(f" Recall: {recall*100:.1f}%")
    print(f" Accuracy: {accuracy*100:.1f}%")
    print(f" F1 Score: {f1:.3f}")

    if infer_times:
        print("-"*50)
        print(f" 推論時間 (最小/最大/平均): {min(infer_times):.3f}s / {max(infer_times):.3f}s / {sum(infer_times)/len(infer_times):.3f}s")

    print(f"\n📁 詳細ログ: {csv_path}")
    print("="*50)

    if f1 >= 0.8:
        print("✅ 判定: このシステムは実用レベルの信頼性を有します。")
        print("   「無理だろ」と言ったクソ上司に、このデータを叩きつけてやれ。")
    else:
        print("⚠️ 判定: 要改善。更なる撮影条件の最適化を推奨します。")

if __name__ == "__main__":
    main()
