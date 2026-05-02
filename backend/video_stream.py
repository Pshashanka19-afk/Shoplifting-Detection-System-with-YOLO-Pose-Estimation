import cv2
from ultralytics import YOLO
from realtime_detector import classify_sequence

print("STARTED")

model = YOLO("yolov8n-pose.pt")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Camera not opening")
    exit()
else:
    print("✅ Camera opened")

sequence = []
history  = []

HISTORY_LEN  = 15
SEQUENCE_LEN = 20

FRAME_PATH  = "latest_frame.jpg"
STATUS_PATH = "latest_status.txt"

with open(STATUS_PATH, "w") as f:
    f.write("NORMAL")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame not received")
        break

    results = model(frame, verbose=False)
    detected = False

    if results[0].keypoints is not None:
        keypoints = results[0].keypoints.xy.cpu().numpy()

        if len(keypoints) > 0:
            kp = keypoints[0]
            sequence.append(kp)

            if len(sequence) > SEQUENCE_LEN:
                sequence.pop(0)

            if len(sequence) == SEQUENCE_LEN:
                detected = True
                status, score = classify_sequence(sequence)

                history.append(status)
                if len(history) > HISTORY_LEN:
                    history.pop(0)

                final_status = max(set(history), key=history.count)

                with open(STATUS_PATH, "w") as f:
                    f.write(final_status)

                print(f"{final_status}  score={score}")

                color = (0, 255, 0)
                if final_status == "SUSPICIOUS":
                    color = (0, 200, 255)
                elif final_status == "SHOPLIFTING":
                    color = (0, 0, 255)

                cv2.rectangle(frame, (15, 15), (480, 105), (0, 0, 0), -1)
                cv2.putText(frame, f"STATUS: {final_status}",
                            (25, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)
                cv2.putText(frame, f"Score: {round(score, 2)}",
                            (25, 92), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    if not detected:
        cv2.rectangle(frame, (15, 15), (320, 65), (0, 0, 0), -1)
        cv2.putText(frame, "Waiting for pose...", (25, 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)

    cv2.imwrite(FRAME_PATH, frame)
    cv2.imshow("Shoplifting Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()