#!/usr/bin/env python3
"""
XIAO S3 Sense + YOLOv8 信頼性評価スクリプト
混合行列 (Confusion Matrix) を用いたリアルタイム精度検証
"""

import cv2
import time
from ultralytics import YOLO

# ============================================
# 定数定義
# ============================================
STREAM_URL = "http://192.168.100.101"  # XIAO S3 SenseのIPアドレス
CUP_CLASS_ID = 41
CONF_THRESHOLD = 0.25

def main():
    print(f"【メタ検証開始】XIAOストリーム ({STREAM_URL}) の再現性と混合行列を計測します...")
    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        print("❌ XIAOの動画ストリームに接続できません。IPアドレスと電源を確認してください。")
        return

    model = YOLO("yolov8n.pt")

    # 混合行列用カウンター
    tp, fp, tn, fn = 0, 0, 0, 0
    current_ground_truth = False  # 初期状態はコップなし(False)

    print("📊 計測開始！【キー操作で正解(Ground Truth)を切り替えてください】")
    print("  [t] キー: 今カメラの前にコップが『ある』状態に設定")
    print("  [f] キー: 今カメラの前にコップが『ない』状態に設定")
    print("  [q] キー: 検証を終了して混合行列の最終レポートを出力")

    while cap.isOpened():
        t_start = time.time()
        success, frame = cap.read()
        if not success:
            print("❌ フレーム取得失敗。リトライします...")
            time.sleep(0.5)
            continue

        capture_latency = (time.time() - t_start) * 1000

        # YOLOv8推論
        t_infer = time.time()
        results = model(frame, conf=CONF_THRESHOLD, verbose=False)
        infer_latency = (time.time() - t_infer) * 1000

        # AIの判定結果
        ai_detected = False
        try:
            # 推論結果の安全な処理
            if results and len(results) > 0 and results[0].boxes is not None:
                for box in results[0].boxes:
                    if int(box.cls) == CUP_CLASS_ID:
                        # xyxyテンソルの形状に依存しない安全な変換
                        xyxy = box.xyxy.cpu().numpy().flatten()
                        x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                        ai_detected = True
                        break
        except Exception as e:
            print(f"⚠️ 推論結果の処理中にエラー: {e}")
            continue

        # 混合行列のリアルタイム集計
        if current_ground_truth == True and ai_detected == True:
            tp += 1
        elif current_ground_truth == False and ai_detected == True:
            fp += 1
        elif current_ground_truth == False and ai_detected == False:
            tn += 1
        elif current_ground_truth == True and ai_detected == False:
            fn += 1

        # 画面へのメトリクス描画
        fps = 1.0 / (time.time() - t_start) if (time.time() - t_start) > 0 else 0
        gt_str = "CUP PRESENT" if current_ground_truth else "CUP ABSENT"

        cv2.putText(frame, f"FPS: {fps:.1f} | Net: {capture_latency:.1f}ms | YOLO: {infer_latency:.1f}ms",
                    (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(frame, f"Ground Truth (Your Input): {gt_str}",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Matrix -> TP:{tp} FP:{fp} TN:{tn} FN:{fn}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        cv2.imshow("XIAO S3 Sense - Reliability & Confusion Matrix Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('t'):
            current_ground_truth = True
        elif key == ord('f'):
            current_ground_truth = False

    cap.release()
    cv2.destroyAllWindows()

    # 最終エビデンスレポート
    total = tp + fp + tn + fn
    print("\n" + "="*50)
    print("📊 クソ上司論破用：混合行列 最終レポート")
    print("="*50)
    print(f" 総サンプル数: {total}")
    print(f" TP (正しく検知): {tp} 回")
    print(f" FP (誤検知・空振り): {fp} 回")
    print(f" TN (正しくスルー): {tn} 回")
    print(f" FN (見落とし): {fn} 回")
    print("-"*50)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / total if total > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    print(f" 適合率 (Precision) : {precision*100:.1f} %")
    print(f"   → 「AIがコップありと判定した時、実際にある確率」")
    print(f" 再現率 (Recall)    : {recall*100:.1f} %")
    print(f"   → 「実際にコップがある時、AIが見逃さない確率」")
    print(f" 正解率 (Accuracy)  : {accuracy*100:.1f} %")
    print(f" F1スコア           : {f1_score:.3f}")
    print(f"   → PrecisionとRecallの調和平均（総合指標）")
    print("="*50)

    if f1_score >= 0.8:
        print("✅ 判定: このシステムは十分な信頼性を有します。")
        print("   「無理だろ」と言ったクソ上司に、このデータを叩きつけてやれ。")
    else:
        print("⚠️ 判定: 要改善。照明やカメラ角度を調整し、再テストを推奨します。")

if __name__ == "__main__":
    main()
