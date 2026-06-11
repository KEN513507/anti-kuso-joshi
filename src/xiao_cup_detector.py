import cv2
from ultralytics import YOLO

# XIAOのIPアドレス
STREAM_URL = "http://192.168.100.101"
CUP_CLASS_ID = 41  # YOLOのコップのクラスID

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(STREAM_URL)

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    results = model(frame, verbose=False)

    for box in results[0].boxes:
        if int(box.cls[0]) == CUP_CLASS_ID:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 3)
            cv2.putText(frame, "☕ CUP", (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

    cv2.imshow("XIAO Sense Cup Detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Test finished.")
