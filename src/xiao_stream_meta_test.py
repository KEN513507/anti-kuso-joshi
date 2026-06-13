import cv2
import time
import numpy as np
from ultralytics import YOLO

# XIAO S3 Sense の生の動画ストリームURL（ポート81を指定）
STREAM_URL = "http://192.168.100"
CUP_CLASS_ID = 41

def main():
    print(f"【メタ検証開始】XIAOストリーム ({STREAM_URL}) の再現性と混合行列を計測します...")
    cap = cv2.VideoCapture(STREAM_URL)

    if not cap.isOpened():
        print("❌ XIAOの動画ストリームに接続できません。URLとWi-Fi接続を確認してください。")
        return

    # device='cpu' を明示的に指定してCUDA警告の発生を抑止
    model = YOLO("yolov8n.pt")

    # 混合行列（Confusion Matrix）用カウンター
    tp, fp, tn, fn = 0, 0, 0, 0
    current_ground_truth = False # 初期状態はコップなし(False)

    print("\n📊 計測開始！【キー操作で正解(Ground Truth)を切り替えてください】")
    print("  [t] キー: 今カメラの前にコップが『ある』状態に設定")
    print("  [f] キー: 今カメラの前にコップが『ない』状態に設定")
    print("  [q] キー: 検証を終了して混合行列の最終レポートを出力\n")

    while cap.isOpened():
        t_start = time.time()
        success, frame = cap.read()
        if not success:
            print("❌ フレーム取得失敗")
            break

        capture_latency = (time.time() - t_start) * 1000

        # 推論を実行（device='cpu' でCUDAエラー/警告を完全にバイパス）
        t_infer = time.time()
        results = model(frame, conf=0.25, verbose=False, device='cpu')
        infer_latency = (time.time() - t_infer) * 1000

        # AIの判定結果
        ai_detected = False

        # results[0].boxes で1フレーム内の全検出ボックスを安全にループ
        for box in results[0].boxes:
            if int(box.cls[0]) == CUP_CLASS_ID:
                # 【ValueErrorの根本治療】
                # テンソルから [0] で1番目の要素を抜き出し、.tolist() でPythonのピュアな配列に変換してからint化
                xyxy = box.xyxy[0].tolist()
                x1, y1, x2, y2 = int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])

                # 安全に枠を描画
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
                ai_detected = True
                break

        # 混合行列のリアルタイム集計
        if current_ground_truth == True and ai_detected == True:   tp += 1 # True Positive
        elif current_ground_truth == False and ai_detected == True: fp += 1 # False Positive
        elif current_ground_truth == False and ai_detected == False: tn += 1 # True Negative
        elif current_ground_truth == True and ai_detected == False:  fn += 1 # False Negative

        # 画面へのメトリクス描画
        fps = 1.0 / (time.time() - t_start)
        gt_str = "CUP PRESENT" if current_ground_truth else "CUP ABSENT"

        cv2.putText(frame, f"FPS: {fps:.1f} | Net: {capture_latency:.1f}ms | YOLO: {infer_latency:.1f}ms", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(frame, f"Ground Truth (Your Input): {gt_str}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Matrix -> TP:{tp} FP:{fp} TN:{tn} FN:{fn}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        cv2.imshow("XIAO S3 Sense - Reliability & Confusion Matrix Test", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'): break
        elif key == ord('t'): current_ground_truth = True
        elif key == ord('f'): current_ground_truth = False

    cap.release()
    cv2.destroyAllWindows()

    # 最終エビデンスレポート
    print("\n" + "="*40)
    print("📊 クソ上司論破用：混合行列 最終レポート")
    print("="*40)
    print(f" 正解が【ある】時に正しく検知 (TP): {tp} 回")
    print(f" 正解が【ない】時に誤検知   (FP): {fp} 回")
    print(f" 正解が【ない】時に正しくスルー(TN): {tn} 回")
    print(f" 正解が【ある】時に見落とし   (FN): {fn} 回")
    print("-"*40)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    accuracy = (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn) > 0 else 0

    print(f" 適合率 (Precision) : {precision*100:.1f} % (無駄な誤警報の少なさ)")
    print(f" 再現率 (Recall)    : {recall*100:.1f} % (上司接近の見落としにくさ)")
    print(f" 正解率 (Accuracy)  : {accuracy*100:.1f} % (総合的な信頼度)")
    print("="*40)

if __name__ == "__main__":
    main()
