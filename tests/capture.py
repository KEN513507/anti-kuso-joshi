import cv2

URL = "http://192.168.100.101/stream"

cap = cv2.VideoCapture(URL)

if not cap.isOpened():
    print("OPEN FAILED")
    raise SystemExit(1)

ret, frame = cap.read()

if not ret:
    print("FRAME FAILED")
    raise SystemExit(1)

cv2.imwrite("captures/capture.jpg", frame)

print("SAVED")

cap.release()