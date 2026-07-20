from playwright.sync_api import sync_playwright
import yaml
import os
import time

class WhatsAppSession:

    def __init__(self):

        with open("config/whatsapp.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        self.personal_chat = self.config["personal_chat"]

        self.headless = self.config["browser"]["headless"]

        self.profile = "browser/whatsapp_profile"

        os.makedirs(self.profile, exist_ok=True)

        self.playwright = None
        self.context = None
        self.page = None

    def open(self):

        print("=" * 60)
        print("Opening WhatsApp Session")
        print("=" * 60)

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.profile,
            headless=self.headless,
            args=["--start-maximized"],
            no_viewport=True,
            viewport=None,
        )

        self.page = (
            self.context.pages[0]
            if self.context.pages
            else self.context.new_page()
        )

        self.page.goto(
            "https://web.whatsapp.com",
            wait_until="domcontentloaded"
        )

        search = self.page.get_by_role("textbox").first
        search.wait_for(timeout=60000)

        print("WhatsApp Ready")

    def open_chat(self, chat_name):

        print("=" * 60)
        print(f"Opening Chat : {chat_name}")
        print("=" * 60)

        search = self.page.get_by_role("textbox").first

        search.click()
        search.fill("")
        search.press_sequentially(chat_name, delay=30)

        self.page.wait_for_timeout(2000)

        search_name = chat_name.split("(")[0].strip()

        chat = self.page.locator(
            f'span[title="{search_name}"]'
        )

        if chat.count() == 0:
            raise Exception(f"Chat '{search_name}' not found.")

        chat.first.click()

        header = self.page.get_by_test_id("conversation-header")
        header.wait_for(timeout=10000)

        header_text = header.inner_text()

        print(f"Opened Chat : {header_text}")

        if search_name.lower() not in header_text.lower():
            raise Exception(
                f"Wrong chat opened. Expected '{search_name}' but found '{header_text}'"
            )

        print("Chat opened successfully")

           

    def send_image(self, image_path):

        print("=" * 60)
        print(f"Sending Image : {image_path}")
        print("=" * 60)

        if not os.path.exists(image_path):
            raise Exception(f"Image not found: {image_path}")

        print("Opening attachment menu...")

        attach_button = self.page.get_by_role("button", name="Attach")
        attach_button.wait_for(timeout=10000)
        attach_button.click()

        photos_option = self.page.get_by_text(
            "Photos & videos",
            exact=True
        )

        photos_option.wait_for(timeout=10000)
        #photos_option.click()

        print("Uploading image...")

        file_input = self.page.locator(
            'input[type="file"][accept*="video"]'
        )

        file_input.set_input_files(image_path)

        # ---------------------------
        # Wait for preview screen
        # ---------------------------
        self.page.wait_for_timeout(3000)

        # ---------------------------
        # Wait for Send button
        # ---------------------------
        send_locator = self.page.get_by_role("button", name="Send")

        send_button = None
        deadline = time.time() + 20

        while time.time() < deadline:

            for i in range(send_locator.count()):
                btn = send_locator.nth(i)
                if btn.is_visible():
                    send_button = btn
                    break

            if send_button:
                break

            self.page.wait_for_timeout(300)

        if not send_button:
            self.page.screenshot(path="debug_send_missing.png")
            raise Exception("Send button not found")

        print("Sending image...")

        send_button.click()

        self.page.wait_for_timeout(3000)

        print("Image sent successfully ✔")
                
        
    def close(self):

        print("Closing WhatsApp Session")

        if self.context:
            self.context.close()

        if self.playwright:
            self.playwright.stop()
