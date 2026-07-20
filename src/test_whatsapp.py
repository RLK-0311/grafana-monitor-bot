import os
from whatsapp_sender import WhatsAppSender

sender = WhatsAppSender()

# FIX: use REAL existing file
IMAGE_PATH = os.path.join(
    os.getcwd(),
    "debug_preview_before_send.png"
)

try:
    sender.send_message(
        message="🚨 Grafana Alert Triggered\nCPU usage high",
        image_path=IMAGE_PATH
    )

    print("=" * 60)
    print("SUCCESS: Message Sent")
    print("=" * 60)

except Exception as e:
    print("ERROR:", e)
