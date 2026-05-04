# Shoplifting Detection System 

An AI-powered shoplifting detection system using **FastAPI** and **YOLOv8 Pose Estimation**.

## Setup Instructions

1. **Install Python 3.8+**
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Download the Model:**
   Ensure `yolov8n-pose.pt` is in the root directory.
4. **Run the Backend:**
   ```bash
   python main.py
   ```
5. **Open the Frontend:**
   Open `Shoplifting.html` in your browser.

##  Project Structure
- `main.py`: FastAPI server and API endpoints.
- `video_stream.py`: Real-time AI processing logic.
- `Shoplifting.html`: Modern dashboard for monitoring.
- `auth.py`: User authentication and registration.

## 🔐 Security Note
By default, the frontend connects to `http://localhost:8000`. If using **ngrok**, update the `API` constant in `Shoplifting.html`.
