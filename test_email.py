from dotenv import load_dotenv
import os

load_dotenv()

print("SMTP_SERVER =", os.getenv("SMTP_SERVER"))
print("SMTP_PORT =", os.getenv("SMTP_PORT"))
print("EMAIL_USERNAME =", os.getenv("EMAIL_USERNAME"))
print("EMAIL_PASSWORD =", os.getenv("EMAIL_PASSWORD"))
