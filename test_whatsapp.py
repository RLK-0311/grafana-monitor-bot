import os
from src.whatsapp import WhatsAppSender

sender = WhatsAppSender()

IMAGE_PATH = os.path.join(
    os.getcwd(),
    "screenshots",
    "CM-CRON.png"  # <-- change this to a real filename from `ls screenshots`
)

sender.send_message(
    chat_name=sender.personal_chat,
    message="",
    image_path=IMAGE_PATH
)
