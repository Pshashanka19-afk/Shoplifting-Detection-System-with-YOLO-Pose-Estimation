from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import time
import numpy as np
import os
import subprocess
import uvicorn
from auth import register_step1, register_step2, login, forgot_step1, forgot_step2

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRAME_PATH = "latest_frame.jpg"
STATUS_PATH = "latest_status.txt"

_logged_in_user = None
_video_process = None

class RegisterStep1Request(BaseModel):
    name: str
    age: int
    mobile: str
    purpose: str
    password: str

class OTPVerifyRequest(BaseModel):
    mobile: str
    otp: str

class LoginRequest(BaseModel):
    mobile: str
    password: str

class ForgotStep1Request(BaseModel):
    mobile: str

class ForgotStep2Request(BaseModel):
    mobile: str
    otp: str
    new_password: str

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/logo.png")
def get_logo():
    if os.path.exists("logo.png"):
        return FileResponse("logo.png")
    return {"error": "logo not found"}

@app.post("/register/step1")
def api_register_step1(req: RegisterStep1Request):
    result = register_step1(req.name, req.age, req.mobile, req.purpose, req.password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/register/step2")
def api_register_step2(req: OTPVerifyRequest):
    result = register_step2(req.mobile, req.otp)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/login")
def api_login(req: LoginRequest):
    global _logged_in_user
    result = login(req.mobile, req.password)
    if not result["success"]:
        raise HTTPException(status_code=401, detail=result["message"])
    _logged_in_user = result["user"]
    return result

@app.post("/forgot/step1")
def api_forgot_step1(req: ForgotStep1Request):
    result = forgot_step1(req.mobile)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/forgot/step2")
def api_forgot_step2(req: ForgotStep2Request):
    result = forgot_step2(req.mobile, req.otp, req.new_password)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/status")
def get_status():
    if _logged_in_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    status = "NORMAL"
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, "r") as f:
            status = f.read().strip()
    return {"status": status, "user": _logged_in_user["name"]}

@app.post("/start_detection")
def start_detection():
    global _video_process
    if _logged_in_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    
    if _video_process is not None and _video_process.poll() is None:
        return {"message": "Detection already running"}
    
    # Start video_stream.py as a subprocess
    _video_process = subprocess.Popen(["python", "video_stream.py"], shell=False)
    return {"message": "Detection started"}

@app.post("/stop_detection")
def stop_detection():
    global _video_process
    if _video_process:
        _video_process.terminate()
        _video_process = None
        return {"message": "Detection stopped"}
    return {"message": "Detection not running"}

def gen_frames():
    while True:
        if os.path.exists(FRAME_PATH):
            with open(FRAME_PATH, "rb") as f:
                frame = f.read()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # Send a placeholder if no frame yet
            img = np.zeros((480, 640, 3), np.uint8)
            cv2.putText(img, "Waiting for camera...", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.05)

@app.get("/video")
def video_feed():
    if _logged_in_user is None:
        raise HTTPException(status_code=401, detail="Not logged in")
    return StreamingResponse(gen_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)