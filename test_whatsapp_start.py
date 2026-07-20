from src.whatsapp import WhatsAppSender

sender = WhatsAppSender()

sender.start()
sender.open_chat(sender.personal_chat)

print("Chat opened successfully. Browser will stay open for 5 seconds...")
sender.page.wait_for_timeout(5000)

sender.close()

print("Done.")
