"""Standard Drive mount helper for Colab notebooks."""
import os

TRIAGE_ROOT = '/content/drive/MyDrive/setique/triage'

def mount_and_get_root():
    from google.colab import drive
    drive.mount('/content/drive', force_remount=False)
    os.makedirs(TRIAGE_ROOT, exist_ok=True)
    return TRIAGE_ROOT
