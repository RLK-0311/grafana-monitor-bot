from playwright.sync_api import sync_playwright
import yaml
import os

from src.whatsapp_upload import upload_images


class WhatsAppSender:
    def __init__(self):
        with open("config/whatsapp.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        self.personal_chat = self.config["personal_chat"]
        self.group_chat = self.config.get("group_chat")

        self.headless = self.config["browser"]["headless"]

        self.profile = "browser/whatsapp_profile"

        os.makedirs(self.profile, exist_ok=True)

        self.playwright = None
        self.context = None
        self.page = None

    # ----------------------------------------------------------------
    # Lifecycle
    # ----------------------------------------------------------------

    def start(self):
        """
        Launches the browser once and loads WhatsApp Web. Call this
        exactly once before open_chat()/send_message()/send_image().
        """
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

        print("Opening WhatsApp...")

        self.page.goto(
            "https://web.whatsapp.com",
            wait_until="domcontentloaded"
        )

        print("Waiting for WhatsApp to load...")

        search = self.page.get_by_role("textbox").first

        try:
            search.wait_for(timeout=60000)
        except Exception:
            self.page.screenshot(
                path="debug_whatsapp_load_failed.png",
                full_page=True
            )
            print(
                "WhatsApp failed to load — saved "
                "debug_whatsapp_load_failed.png"
            )
            raise

        print("WhatsApp Loaded Successfully")

    def close(self):
        """
        Closes the browser and stops Playwright. Call this once, after
        all messages/images have been sent.

        context.close() and playwright.stop() are wrapped individually
        so that a failure in one (e.g. the context already gone because
        the browser crashed mid-run) doesn't stop playwright.stop() from
        still running — and doesn't propagate out of close() and mask
        whatever the real error in the calling code was.
        """
        try:
            if self.context:
                self.context.close()
        except Exception as e:
            print(f"Context close warning: {e}")

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"Playwright stop warning: {e}")

        self.page = None
        self.context = None
        self.playwright = None

    # ----------------------------------------------------------------
    # Chat selection
    # ----------------------------------------------------------------

    def open_chat(self, chat_name):
        """
        Searches for and opens the given chat. Call this once per chat
        you want to send to — you can call send_image()/send_message()
        multiple times after a single open_chat() call, as long as
        you're sending to the same chat.
        """
        print(f"Searching chat: {chat_name}")

        search = self.page.get_by_role("textbox").first
        search.click()
        search.fill("")
        search.press_sequentially(chat_name, delay=30)

        self.page.wait_for_timeout(2000)

        print("Selecting chat...")

        search_name = chat_name.split("(")[0].strip()

        chat = self.page.locator(f'span[title="{search_name}"]')

        if chat.count() == 0:
            raise Exception(f"Chat '{search_name}' not found.")

        chat.first.click()

        header = self.page.get_by_test_id("conversation-header")
        header.wait_for(timeout=10000)
        header_text = header.inner_text()

        print(f"Opened Chat : {header_text}")

        if search_name.lower() not in header_text.lower():
            raise Exception(
                f"Wrong chat opened. Expected '{search_name}' "
                f"but found '{header_text}'"
            )

    # ----------------------------------------------------------------
    # Sending
    # ----------------------------------------------------------------

    def send_message(self, message):
        """
        Sends a plain text message to whichever chat is currently open
        (call open_chat() first).
        """
        message_box = self.page.get_by_role("textbox").last
        message_box.wait_for(timeout=10000)
        message_box.click()

        lines = message.split("\n")
        for i, line in enumerate(lines):
            message_box.press_sequentially(line, delay=10)
            if i != len(lines) - 1:
                self.page.keyboard.down("Shift")
                self.page.keyboard.press("Enter")
                self.page.keyboard.up("Shift")

        self.page.keyboard.press("Enter")
        self.page.wait_for_timeout(2000)

        print("=" * 60)
        print("Message Sent Successfully")
        print("=" * 60)

    def send_images(self, image_paths):
        """
        Uploads and sends an image to whichever chat is currently open
        (call open_chat() first). Delegates to the already-working
        upload_images() logic in whatsapp_upload.py, unchanged.
        """
        upload_images(
            self.page,
            image_paths
        )