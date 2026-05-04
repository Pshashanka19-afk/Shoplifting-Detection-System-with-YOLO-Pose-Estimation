import sys
try:
    import main
    print("Main module imported successfully!")
    print(f"App instance: {main.app}")
except Exception as e:
    import traceback
    traceback.print_exc()
