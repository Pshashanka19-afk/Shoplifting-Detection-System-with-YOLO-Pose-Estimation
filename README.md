<div align="center">
  
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=200&section=header&text=Shoplifting%20Detection%20System&fontSize=50&fontAlignY=38&desc=Powered%20by%20AI%20&%20YOLOv8%20Pose%20Estimation&descAlignY=60&descAlign=62" />

  **An intelligent, real-time AI surveillance system designed to protect retail environments by predicting and detecting shoplifting behaviors before they happen.**

  ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
  ![YOLOv8](https://img.shields.io/badge/YOLOv8-FFD700?style=for-the-badge&logo=yolo&logoColor=black)
  ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
  ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

</div>



##  The Problem ##
Retail shrinkage costs the industry *billions of dollars annually*. Traditional security cameras rely entirely on human monitoring, which is prone to fatigue, distraction, and blind spots. By the time a theft is noticed, it's often too late.

## The Solution ##
Meet the **AI Shoplifting Detection System**. Using cutting-edge **YOLOv8 Pose Estimation**, this system doesn't just record video—it actively *understands* human behavior. By analyzing skeletal movements in real-time, the AI flags suspicious sequences (like reaching, hiding items, or abnormal lingering) and instantly alerts staff via a stunning web dashboard and SMS.



## Why This Project Stands Out ##

**State-of-the-Art AI:** Utilizes `yolov8n-pose.pt` to process high-speed video feeds and extract real-time human pose coordinates.  
**Lightning Fast:** Built on **FastAPI** to handle concurrent video streaming and API requests without breaking a sweat.  
**Beautiful UI/UX:** A stunning, Glassmorphism-inspired single-page frontend (`Shoplifting.html`) that looks straight out of a sci-fi movie.  
**Enterprise-Grade Access:** Role-based access control (RBAC) ensures only administrators can view sensitive history, all protected behind secure authentication.  
**Instant Alerts:** Integrated mock SMS notification pipeline to simulate real-world security dispatches.  



## 📸 Sneak Peek
> **Tip for the creator:** Add a `.gif` or screenshot of your working dashboard here! 
> 
> *(Example syntax: `![Dashboard Screenshot](path/to/image.png)`)*

---

Technology Stack

| Domain | Tech |
| ------ | ---- |
| **Backend** | Python, FastAPI, Uvicorn |
| **AI / ML** | Ultralytics YOLOv8, OpenCV, NumPy |
| **Frontend** | HTML5, CSS3 (Glassmorphism), Vanilla JS |
| **Communication**| AJAX, Fetch API, Simulated SMS |

---

## Quick Start Guide

Want to run this locally? Follow these steps to get your AI guard up and running in minutes.

### Clone the Repository
```bash
git clone https://github.com/Pshashanka19-afk/Shoplifting-Detection-System-with-YOLO-Pose-Estimation.git
cd Shoplifting-Detection-System-with-YOLO-Pose-Estimation/backend
```

### Install the Arsenal (Dependencies)
Ensure you have Python 3.8+ installed.
```bash
pip install -r requirements.txt
```

## Equip the AI Brain
Ensure the YOLOv8 pose model (`yolov8n-pose.pt`) is in your `backend` directory. *(If missing, Ultralytics usually downloads it automatically on the first run).*

## Ignite the Backend
```bash
python main.py
```
> The API will now be listening on `http://127.0.0.1:8000`.

##Launch the Command Center
Double-click `Shoplifting.html` to open it in your browser. Log in, connect your camera, and watch the AI work its magic!

---

## How It Works (Under the Hood)
1. **Video Ingestion:** `video_stream.py` captures the live feed.
2. **Pose Extraction:** The frame is passed to the YOLOv8 model in `realtime_detector.py`.
3. **Behavior Analysis:** Coordinates are analyzed over sequential frames to detect patterns of concealment or theft.
4. **Alert Trigger:** If a threshold is crossed, a "Shoplifting Detected" status is saved, and SMS alerts are queued.
5. **Dashboard Sync:** The frontend continuously polls `/status` and `/video`, updating the UI with red alerts instantly.

---

## Network Configuration
Building for a hackathon or remote demo? If you expose your FastAPI backend using a tool like **ngrok**, simply open `Shoplifting.html` and update the `API` variable at the top of the script to match your public URL.

---

<div align="center">
  <h3>Ready to secure the future of retail? Star this repository!</h3>
  <p>Contributions, issues, and feature requests are welcome!</p>
</div>
