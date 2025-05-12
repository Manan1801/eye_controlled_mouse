import subprocess

def open_chrome():
    """Open Google Chrome application."""
    subprocess.Popen(["open", "-a", "Google Chrome"])

def open_telegram():
    """Open Telegram application."""
    subprocess.Popen(["open", "-a", "Telegram"])

def launch_application(blinked_eye):
    """Launch application based on the eye that was blinked."""
    if blinked_eye == 'left':
        open_chrome()
    elif blinked_eye == 'right':
        open_telegram()