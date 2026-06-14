import cv2
import threading
import time
import psutil
import os
import sys
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
from ultralytics import YOLO

# ============================================
# Anti-Kuso-Joshi: app.py
# ============================================

app = FastAPI(title="Anti-Kuso-Joshi System")

# Constants
STREAM_URL = "http://192.168.100.101/stream"
MODEL_PATH = "yolov8n.pt"

class SystemState:
    def __init__(self):
        self.raw_frame = None
        self.processed_frame = None
        self.inference_results = None
        self.fps = 0.0
        self.inference_time = 0.0
        self.detection_count = 0
        self.lock = threading.Lock()
        self.running = True
        
        # YOLOv8n Load (CPU Only)
        print(f"[SYSTEM] Loading YOLOv8n on CPU...")
        self.model = YOLO(MODEL_PATH)

state = SystemState()

def stream_receiver():
    """ESP32からのMJPEGストリームを受信し、最新の1フレームを保持する"""
    print(f"[STREAM] Connecting to {STREAM_URL}...")
    cap = cv2.VideoCapture(STREAM_URL)
    
    while state.running:
        ret, frame = cap.read()
        if not ret:
            print("[STREAM] Connection lost. Reconnecting...")
            time.sleep(2)
            cap.open(STREAM_URL)
            continue
        
        with state.lock:
            state.raw_frame = frame
            # print("[LOG] Frame Received") # 高負荷回避のため通常はコメントアウト

def inference_worker():
    """最新フレームに対して推論を実行する。完了後に次を処理。"""
    print("[AI] Inference Worker Started (Device: CPU)")
    while state.running:
        frame = None
        with state.lock:
            if state.raw_frame is not None:
                frame = state.raw_frame.copy()
        
        if frame is not None:
            start_time = time.time()
            
            # 推論 (classes指定禁止、CPU固定)
            results = state.model(frame, device="cpu", verbose=False)
            
            end_time = time.time()
            state.inference_time = end_time - start_time
            state.fps = 1.0 / state.inference_time if state.inference_time > 0 else 0
            
            # 結果解析
            res = results[0]
            state.detection_count = len(res.boxes)
            annotated_frame = res.plot()
            
            with state.lock:
                state.processed_frame = annotated_frame
            
            # ログ出力
            mem = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            print(f"[LOG] Inference Finished | Detections: {state.detection_count} | FPS: {state.fps:.2f} | Mem: {mem:.2f} MB")
        else:
            time.sleep(0.01)

@app.on_event("startup")
async def startup_event():
    threading.Thread(target=stream_receiver, daemon=True).start()
    threading.Thread(target=inference_worker, daemon=True).start()

@app.on_event("shutdown")
def shutdown_event():
    state.running = False

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <html>
        <head>
            <title>Anti-Kuso-Joshi Monitor</title>
            <style>
                body { font-family: sans-serif; background: #1a1a1a; color: #eee; text-align: center; }
                .container { margin-top: 20px; }
                #video-feed { border: 2px solid #444; max-width: 100%; }
                .stats { display: flex; justify-content: center; gap: 20px; margin-top: 10px; font-size: 1.2em; }
                .stat-box { background: #333; padding: 10px 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Anti-Kuso-Joshi Live Monitor</h1>
            <div class="container">
                <img id="video-feed" src="/video">
            </div>
            <div class="stats">
                <div class="stat-box">FPS: <span id="fps">0</span></div>
                <div class="stat-box">Detections: <span id="detects">0</span></div>
                <div class="stat-box">Mem: <span id="mem">0</span> MB</div>
            </div>
            <script>
                setInterval(async () => {
                    try {
                        const res = await fetch('/status');
                        const data = await res.json();
                        document.getElementById('fps').innerText = data.fps.toFixed(2);
                        document.getElementById('detects').innerText = data.detections;
                        document.getElementById('mem').innerText = data.memory_mb.toFixed(2);
                    } catch (e) {}
                }, 1000);
            </script>
        </body>
    </html>
    """

def gen_frames():
    while state.running:
        frame_bytes = None
        with state.lock:
            if state.processed_frame is not None:
                ret, buffer = cv2.imencode('.jpg', state.processed_frame)
                if ret:
                    frame_bytes = buffer.tobytes()
        
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.033) # 約30FPSでブラウザに配信

@app.get("/video")
async def video_feed():
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/status")
async def get_status():
    mem = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
    return {
        "fps": state.fps,
        "detections": state.detection_count,
        "memory_mb": mem,
        "inference_time_ms": state.inference_time * 1000
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
