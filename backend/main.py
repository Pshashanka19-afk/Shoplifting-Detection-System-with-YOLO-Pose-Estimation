from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import cv2
import time
import numpy as np
import os
from auth import register_step1, register_step2, login, forgot_step1, forgot_step2

app = FastAPI()

FRAME_PATH  = "latest_frame.jpg"
STATUS_PATH = "latest_status.txt"

_logged_in_user = None


class RegisterStep1Request(BaseModel):
    name    : str
    age     : int
    mobile  : str
    purpose : str
    password: str

class OTPVerifyRequest(BaseModel):
    mobile: str
    otp   : str

class LoginRequest(BaseModel):
    mobile  : str
    password: str

class ForgotStep1Request(BaseModel):
    mobile: str

class ForgotStep2Request(BaseModel):
    mobile      : str
    otp         : str
    new_password: str


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


def require_login():
    if _logged_in_user is None:
        raise HTTPException(status_code=401,
                            detail="Please login first before accessing the camera feed.")

@app.get("/status")
def get_status():
    require_login()
    status = "NORMAL"
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, "r") as f:
            status = f.read().strip()
    return {
        "status": status,
        "user"  : _logged_in_user["name"] if _logged_in_user else None
    }


def gen_frames():
    last_good_frame = None

    # build a blank frame once
    blank_img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(blank_img, "Waiting for camera...", (120, 240),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
    _, blank_buf = cv2.imencode('.jpg', blank_img)
    blank_bytes = blank_buf.tobytes()

    while True:
        frame_bytes = None

        if os.path.exists(FRAME_PATH):
            try:
                with open(FRAME_PATH, "rb") as f:
                    data = f.read()
                # only use frame if it is a valid jpeg
                if len(data) > 100 and data[:2] == b'\xff\xd8':
                    frame_bytes = data
                    last_good_frame = data
            except Exception:
                pass

        # use last good frame if current read failed
        if frame_bytes is None:
            frame_bytes = last_good_frame if last_good_frame else blank_bytes

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)


@app.get("/video")
def video():
    require_login()
    return StreamingResponse(
        gen_frames(),
        media_type='multipart/x-mixed-replace; boundary=frame'
    )