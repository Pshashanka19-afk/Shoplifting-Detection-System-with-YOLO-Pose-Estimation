import threading

current_status  = "NORMAL"
_logged_in_user = None
_latest_frame   = None
_frame_lock     = threading.Lock()


def set_latest_frame(jpeg_bytes: bytes):
    global _latest_frame
    with _frame_lock:
        _latest_frame = jpeg_bytes


def get_latest_frame():
    with _frame_lock:
        return _latest_frame
