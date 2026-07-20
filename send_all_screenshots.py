from pathlib import Path
from src.whatsapp import WhatsAppSender
SCREENSHOT_DIR = Path("screenshots")
sender = WhatsAppSender()
images = sorted(SCREENSHOT_DIR.glob("*.png"))
print("=" * 60)
print(f"Found {len(images)} screenshots")
print("=" * 60)
for index, image in enumerate(images, start=1):
    print(f"\n[{index}/{len(images)}]")
    print(f"Sending: {image.name}")
    sender.send_message(
        chat_name=sender.personal_chat,
        message="",
        image_path=str(image)
    )
print("\nAll screenshots sent successfully.")
