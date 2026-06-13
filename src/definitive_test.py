#!/usr/bin/env python3
"""
Anti-Kuso-Joshi Project: 最終 PoC 検証スクリプト
- GPU非依存のCPU最適化モード
- 推論時間の計測と平均化
- 3フレームスキップによる体感速度向上
- 320x240 強制推論
- CSV 監査ログ & 混合行列レポート
"""

import cv2
import time
import csv
import os
from datetime import datetime
from ultralytics import YOLO

# ============================================
# 定数定義
# ============================================
STREAM_URL = "http://192.168.100.101"
CUP_CLASS_ID = 41
CONF_THRESHOLD = 0.25
INFER_SIZE = (320, 240)  # 推論用解像度
FRAME_SKIP = 3           # 3フレームに1回推論
LOG_DIR = "evidence_logs"

def main():
    print(f"【CPU最適化モード】XIAOストリーム ({STREAM_URL}) の最終評価を開始します...")

    # 監査ログ用ディレクトリ作成
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # CSVログファイルの準備
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(LOG_DIR, f"evidence_{timestamp}.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "GroundTruth", "AIDetected", "InferTime"])

    print(f"📁 監査ログ: {csv_path}")

    # 映像ストリームを開く
    cap = cv2.VideoCapture(STREAM_URL)
    if not cap.isOpened():
        print("❌ XIAOに接続できません。")
        return

    model = YOLO("yolov8n.pt")

    # 混合行列 & 推論時間リスト
    tp, fp, tn, fn = 0, 0, 0, 0
    infer_times = []
    current_ground_truth = False
    frame_count = 0

    print("\n📊 計測を開始します。")
    print("  ターミナルに以下のコマンドを入力してください：")
    print("    t : コップが『ある』状態に切り替え")
    print("    f : コップが『ない』状態に切り替え")
    print("    q : 計測を終了し、レポートを出力")
    print("-" * 50)

    # ユーザー入力用スレッド (waitKey に依存しない)
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

        # ユーザー指示処理
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

        # フレームスキップ (3フレームに1回推論)
        ai_detected = False
        infer_sec = 0.0

        if frame_count % FRAME_SKIP == 0:
            # 推論用に320x240へリサイズ
            infer_frame = cv2.resize(frame, INFER_SIZE)

            # YOLO推論 (時間計測)
            t0 = time.time()
            results = model(infer_frame, conf=CONF_THRESHOLD, verbose=False)
            infer_sec = time.time() - t0
            infer_times.append(infer_sec)

            # AI判定
            try:
                if results and len(results) > 0 and results[0].boxes is not None:
                    for box in results[0].boxes:
                        if int(box.cls) == CUP_CLASS_ID:
                            # 座標を元の解像度にスケーリング
                            xyxy = box.xyxy.cpu().numpy().flatten()
                            scale_x = frame.shape[1] / INFER_SIZE[0]
                            scale_y = frame.shape[0] / INFER_SIZE[1]
                            x1 = int(xyxy[0] * scale_x)
                            y1 = int(xyxy[1] * scale_y)
                            x2 = int(xyxy[2] * scale_x)
                            y2 = int(xyxy[3] * scale_y)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                            ai_detected = True
                            break
            except Exception:
                pass

        # 混合行列集計 & CSV 記録
        if current_ground_truth and ai_detected: tp += 1
        elif not current_ground_truth and ai_detected: fp += 1
        elif not current_ground_truth and not ai_detected: tn += 1
        elif current_ground_truth and not ai_detected: fn += 1

        with open(csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([time.time(), current_ground_truth, ai_detected, f"{infer_sec:.3f}"])

        # 画面描画
        gt_str = "CUP PRESENT" if current_ground_truth else "CUP ABSENT"
        avg_infer = sum(infer_times) / len(infer_times) if infer_times else 0

        cv2.putText(frame, f"YOLO: {infer_sec:.3f}s (avg: {avg_infer:.3f}s)", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, f"GT: {gt_str}", (10, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"TP:{tp} FP:{fp} TN:{tn} FN:{fn}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        cv2.imshow("CPU Optimized PoC", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # 最終レポート
    total = tp + fp + tn + fn
    print("\n" + "="*50)
    print("📊 クソ上司論破用：CPU最適化モード 最終レポート")
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
        print(f" 体感FPS (スキップ後): {1.0 / (sum(infer_times)/len(infer_times)):.1f}")

    print(f"\n📁 詳細ログ: {csv_path}")
    print("="*50)

if __name__ == "__main__":
    main()
