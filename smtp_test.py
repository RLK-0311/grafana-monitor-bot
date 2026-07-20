import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()

msg = MIMEText("SMTP Test")

msg["Subject"] = "SMTP Test"
msg["From"] = os.getenv("EMAIL_USERNAME")
msg["To"] = os.getenv("EMAIL_USERNAME")

try:
    smtp = smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
    smtp.starttls()

    smtp.login(
        os.getenv("EMAIL_USERNAME"),
        os.getenv("EMAIL_PASSWORD")
    )

    smtp.send_message(msg)

    smtp.quit()

    print("SUCCESS")

except Exception as e:
    print(e)
