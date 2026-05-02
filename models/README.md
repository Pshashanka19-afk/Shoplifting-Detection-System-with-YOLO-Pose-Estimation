# Shoplifting Detection System Models

Place your model weights in this directory.

1. **YOLO Pose Model**: `yolov8n-pose.pt`
   - This will be downloaded automatically by the `ultralytics` package upon first run.

2. **Behavior Sequence Model**: `behavior_lstm.h5`
   - This is where you would place your trained LSTM or transformer model for activity classification based on the extracted keypoints.
   - The current backend logic provides a placeholder implementation that mimics this behavior.
