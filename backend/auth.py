import json
import os
import random
import hashlib
from datetime import datetime
from sms import send_otp

# ── File paths ───────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")

os.makedirs(DATA_DIR, exist_ok=True)


# ── OTP store (in memory, valid for session) ─────────────────────
# { "9876543210": {"otp": "4821", "purpose": "register"} }
_otp_store: dict = {}


# ── Password hashing ─────────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


# ── JSON helpers ─────────────────────────────────────────────────
def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)


# ── OTP generator ─────────────────────────────────────────────────
def generate_otp() -> str:
    return str(random.randint(1000, 9999))


# ════════════════════════════════════════════════════════════════
#  REGISTRATION
# ════════════════════════════════════════════════════════════════
def register_step1(name: str, age: int, mobile: str,
                   purpose: str, password: str) -> dict:
    """
    Step 1 of registration.
    Validates input, sends OTP, stores details temporarily.
    """
    # validation
    if len(mobile) != 10 or not mobile.isdigit():
        return {"success": False, "message": "Mobile number must be 10 digits"}

    if len(password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters"}

    users = load_users()
    if mobile in users:
        return {"success": False, "message": "Mobile number already registered. Please login."}

    otp = generate_otp()

    # store temporarily until OTP is verified
    _otp_store[mobile] = {
        "otp"    : otp,
        "purpose": "register",
        "data"   : {
            "name"       : name,
            "age"        : age,
            "mobile"     : mobile,
            "purpose"    : purpose,
            "password"   : hash_password(password),
            "created_at" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    sent = send_otp(mobile, otp)
    if not sent:
        return {"success": False, "message": "Failed to send OTP. Check your Fast2SMS API key."}

    return {"success": True, "message": f"OTP sent to {mobile}. Please verify."}


def register_step2(mobile: str, otp_entered: str) -> dict:
    """
    Step 2: verify OTP and create account.
    """
    if mobile not in _otp_store:
        return {"success": False, "message": "No OTP request found. Please register again."}

    store = _otp_store[mobile]

    if store["purpose"] != "register":
        return {"success": False, "message": "Invalid OTP request."}

    if store["otp"] != otp_entered:
        return {"success": False, "message": "Wrong OTP. Please try again."}

    # save user
    users = load_users()
    users[mobile] = store["data"]
    save_users(users)

    del _otp_store[mobile]

    return {"success": True, "message": "Account created successfully! Please login."}


# ════════════════════════════════════════════════════════════════
#  LOGIN
# ════════════════════════════════════════════════════════════════
def login(mobile: str, password: str) -> dict:
    """
    Verify mobile + password.
    Returns user data on success.
    """
    if len(mobile) != 10 or not mobile.isdigit():
        return {"success": False, "message": "Invalid mobile number"}

    users = load_users()

    if mobile not in users:
        return {"success": False, "message": "Mobile not registered. Please sign up."}

    user = users[mobile]

    if not verify_password(password, user["password"]):
        return {"success": False, "message": "Wrong password. Try again or use Forgot Password."}

    return {
        "success": True,
        "message": f"Welcome back, {user['name']}!",
        "user"   : {
            "name"   : user["name"],
            "age"    : user["age"],
            "mobile" : user["mobile"],
            "purpose": user["purpose"]
        }
    }


# ════════════════════════════════════════════════════════════════
#  FORGOT PASSWORD
# ════════════════════════════════════════════════════════════════
def forgot_step1(mobile: str) -> dict:
    """
    Step 1: send OTP to registered mobile.
    """
    if len(mobile) != 10 or not mobile.isdigit():
        return {"success": False, "message": "Invalid mobile number"}

    users = load_users()

    if mobile not in users:
        return {"success": False, "message": "Mobile not registered. Please sign up."}

    otp = generate_otp()
    _otp_store[mobile] = {
        "otp"    : otp,
        "purpose": "forgot"
    }

    sent = send_otp(mobile, otp)
    if not sent:
        return {"success": False, "message": "Failed to send OTP."}

    return {"success": True, "message": f"OTP sent to {mobile}."}


def forgot_step2(mobile: str, otp_entered: str, new_password: str) -> dict:
    """
    Step 2: verify OTP and set new password.
    """
    if mobile not in _otp_store:
        return {"success": False, "message": "No OTP request found. Please try again."}

    store = _otp_store[mobile]

    if store["purpose"] != "forgot":
        return {"success": False, "message": "Invalid OTP request."}

    if store["otp"] != otp_entered:
        return {"success": False, "message": "Wrong OTP. Please try again."}

    if len(new_password) < 6:
        return {"success": False, "message": "Password must be at least 6 characters"}

    # update password
    users = load_users()
    users[mobile]["password"] = hash_password(new_password)
    save_users(users)

    del _otp_store[mobile]

    return {"success": True, "message": "Password reset successful! Please login."}
