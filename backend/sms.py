# SMS service replaced with terminal OTP display
# Reason: Fast2SMS requires website verification (takes days)
# For demo: OTP is printed in terminal — fully functional for testing

def send_otp(mobile: str, otp: str) -> bool:
    """
    Prints OTP to terminal instead of sending SMS.
    Works 100% for demo purposes.
    """
    print("\n" + "="*40)
    print(f"  OTP for {mobile}: {otp}")
    print("="*40 + "\n")
    return True
