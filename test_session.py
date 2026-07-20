from src.whatsapp_session import WhatsAppSession

session = WhatsAppSession()

try:

    session.open()

    session.open_chat(session.personal_chat)

    session.send_image(
        "screenshots/CM-CRON.png"
    )

    input("\nPress ENTER to close...")

finally:

    session.close()
