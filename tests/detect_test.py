from ultralytics import YOLO
import cv2

model = YOLO("yolov8n.pt")

img = cv2.imread("captures/capture.jpg")

results = model(img)

print("\n=== DETECTIONS ===")

for box in results[0].boxes:

    cls = int(box.cls[0])

    conf = float(box.conf[0])

    name = results[0].names[cls]

    print(
        f"{name} {conf:.3f}"
    )
