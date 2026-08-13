from playwright.sync_api import sync_playwright
import yaml
import os
import time

from src.whatsapp_upload import upload_images


class WhatsAppSender:

    def __init__(self):

        # ---------------------------------------------------------
        # Load WhatsApp configuration
        # ---------------------------------------------------------

        with open("config/whatsapp.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        self.personal_chat = self.config["personal_chat"]
        self.group_chat = self.config.get("group_chat")

        self.headless = self.config["browser"]["headless"]

        # ---------------------------------------------------------
        # Persistent WhatsApp browser profile
        # ---------------------------------------------------------

        self.profile = "browser/whatsapp_profile"

        os.makedirs(self.profile, exist_ok=True)

        # ---------------------------------------------------------
        # Playwright objects
        # ---------------------------------------------------------

        self.playwright = None
        self.context = None
        self.page = None

    # =============================================================
    # START WHATSAPP
    # =============================================================

    def start(self):

        """
        Start Chromium using the persistent WhatsApp profile.

        The persistent profile stores the WhatsApp Web login session,
        so normally you do NOT need to scan the QR code every time.

        This method:
            1. Starts Playwright
            2. Opens Chromium
            3. Loads WhatsApp Web
            4. Waits for WhatsApp to become usable
            5. Detects the search textbox
        """

        print("=" * 70)
        print("Starting WhatsApp...")
        print("=" * 70)

        # ---------------------------------------------------------
        # Start Playwright
        # ---------------------------------------------------------

        self.playwright = sync_playwright().start()

        # ---------------------------------------------------------
        # Launch Chromium with persistent profile
        # ---------------------------------------------------------

        self.context = self.playwright.chromium.launch_persistent_context(

            user_data_dir=self.profile,

            headless=self.headless,

            args=[
                "--start-maximized",
                "--disable-notifications",
            ],

            no_viewport=True,

            viewport=None,
        )

        # ---------------------------------------------------------
        # Get existing page or create a new page
        # ---------------------------------------------------------

        if self.context.pages:

            self.page = self.context.pages[0]

        else:

            self.page = self.context.new_page()

        print("Opening WhatsApp...")

        # ---------------------------------------------------------
        # Navigate to WhatsApp Web
        # ---------------------------------------------------------

        try:

            self.page.goto(
                "https://web.whatsapp.com",
                wait_until="domcontentloaded",
                timeout=60000,
            )

        except Exception as e:

            print(f"WhatsApp navigation warning: {e}")

        print("Waiting for WhatsApp to load...")

        # ---------------------------------------------------------
        # Wait for WhatsApp
        # ---------------------------------------------------------

        loaded = self._wait_for_whatsapp()

        if not loaded:

            self._save_debug_screenshot()

            raise Exception(
                "WhatsApp Web did not become ready."
            )

        print("WhatsApp Loaded Successfully")

    # =============================================================
    # WAIT FOR WHATSAPP
    # =============================================================

    def _wait_for_whatsapp(self):

        """
        Wait for WhatsApp Web to become usable.

        WhatsApp may initially display:

            Loading your chats

        before the search textbox becomes available.

        We therefore check several possible states instead of
        immediately waiting 60 seconds for one locator.
        """

        timeout_seconds = 120

        start_time = time.time()

        print(
            f"Waiting up to {timeout_seconds} seconds "
            "for WhatsApp..."
        )

        while time.time() - start_time < timeout_seconds:

            try:

                # -------------------------------------------------
                # Check whether page is still alive
                # -------------------------------------------------

                if self.page.is_closed():

                    print("WhatsApp page was closed.")

                    return False

                # -------------------------------------------------
                # Current URL
                # -------------------------------------------------

                current_url = self.page.url

                print(
                    f"WhatsApp URL: {current_url}"
                )

                # -------------------------------------------------
                # Search textbox
                # -------------------------------------------------

                textboxes = self.page.get_by_role(
                    "textbox"
                )

                textbox_count = textboxes.count()

                if textbox_count > 0:

                    for i in range(textbox_count):

                        try:

                            textbox = textboxes.nth(i)

                            if textbox.is_visible():

                                print(
                                    "WhatsApp search textbox "
                                    "is visible."
                                )

                                return True

                        except Exception:
                            continue

                # -------------------------------------------------
                # Check common WhatsApp elements
                # -------------------------------------------------

                selectors = [

                    '[data-testid="chat-list-search"]',

                    '[data-testid="search"]',

                    '[contenteditable="true"]',

                    'div[role="textbox"]',

                ]

                for selector in selectors:

                    try:

                        locator = self.page.locator(
                            selector
                        )

                        count = locator.count()

                        if count > 0:

                            for i in range(count):

                                try:

                                    element = locator.nth(i)

                                    if element.is_visible():

                                        print(
                                            f"WhatsApp ready "
                                            f"using selector: "
                                            f"{selector}"
                                        )

                                        return True

                                except Exception:
                                    continue

                    except Exception:
                        continue

                # -------------------------------------------------
                # Detect QR code
                # -------------------------------------------------

                qr_selectors = [

                    'canvas',

                    '[data-ref]',

                ]

                qr_detected = False

                for selector in qr_selectors:

                    try:

                        if self.page.locator(
                            selector
                        ).count() > 0:

                            qr_detected = True
                            break

                    except Exception:
                        pass

                if qr_detected:

                    print(
                        "WhatsApp login screen detected."
                    )

                    print(
                        "If QR code is displayed, "
                        "scan it using your phone."
                    )

                # -------------------------------------------------
                # Detect loading screen
                # -------------------------------------------------

                try:

                    body_text = self.page.locator(
                        "body"
                    ).inner_text(
                        timeout=3000
                    )

                    if "Loading your chats" in body_text:

                        print(
                            "WhatsApp is still loading..."
                        )

                    elif "Use WhatsApp on your computer" in body_text:

                        print(
                            "WhatsApp login screen detected."
                        )

                except Exception:
                    pass

            except Exception as e:

                print(
                    f"WhatsApp readiness check warning: {e}"
                )

            # -----------------------------------------------------
            # Wait before checking again
            # -----------------------------------------------------

            self.page.wait_for_timeout(3000)

        print(
            "WhatsApp did not become ready "
            f"within {timeout_seconds} seconds."
        )

        return False

    # =============================================================
    # DEBUG SCREENSHOT
    # =============================================================

    def _save_debug_screenshot(self):

        """
        Save a screenshot when WhatsApp fails to load.

        This helps diagnose:
            - WhatsApp loading problems
            - QR login problems
            - Browser problems
            - Network problems
            - Profile problems
        """

        try:

            path = "debug_whatsapp_load_failed.png"

            self.page.screenshot(
                path=path,
                full_page=True
            )

            print(
                f"WhatsApp failed to load — "
                f"saved {path}"
            )

        except Exception as e:

            print(
                f"Could not save WhatsApp debug screenshot: {e}"
            )

    # =============================================================
    # OPEN CHAT
    # =============================================================

    def open_chat(self, chat_name):

        """
        Search for and open a WhatsApp chat.

        Example:

            open_chat("SonJIO (You)")

        The browser session must already be started using:

            start()
        """

        if not self.page:

            raise Exception(
                "WhatsApp browser is not started. "
                "Call start() first."
            )

        print("=" * 70)
        print(
            f"Searching WhatsApp chat: {chat_name}"
        )
        print("=" * 70)

        # ---------------------------------------------------------
        # Find search textbox
        # ---------------------------------------------------------

        search = self._get_search_box()

        if search is None:

            raise Exception(
                "WhatsApp search textbox not found."
            )

        # ---------------------------------------------------------
        # Click search
        # ---------------------------------------------------------

        search.click()

        # ---------------------------------------------------------
        # Clear existing search
        # ---------------------------------------------------------

        try:

            search.fill("")

        except Exception:

            search.press("Control+A")
            search.press("Backspace")

        # ---------------------------------------------------------
        # Type chat name
        # ---------------------------------------------------------

        search.press_sequentially(
            chat_name,
            delay=30
        )

        # ---------------------------------------------------------
        # Wait for search results
        # ---------------------------------------------------------

        self.page.wait_for_timeout(5000)

        print("Selecting chat...")

        # ---------------------------------------------------------
        # Extract actual chat name
        #
        # Example:
        #
        # SonJIO (You)
        #
        # becomes:
        #
        # SonJIO
        # ---------------------------------------------------------

        search_name = chat_name.split("(")[0].strip()

        # ---------------------------------------------------------
        # Try exact title
        # ---------------------------------------------------------

        chat = self.page.locator(
            f'span[title="{search_name}"]'
        )

        try:

            count = chat.count()

        except Exception:

            count = 0

        # ---------------------------------------------------------
        # If exact title wasn't found, try text
        # ---------------------------------------------------------

        if count == 0:

            print(
                "Exact chat title not found. "
                "Trying text search..."
            )

            chat = self.page.get_by_text(
                search_name,
                exact=True
            )

            try:

                count = chat.count()

            except Exception:

                count = 0

        # ---------------------------------------------------------
        # Chat not found
        # ---------------------------------------------------------

        if count == 0:

            self._save_debug_screenshot()

            raise Exception(
                f"Chat '{search_name}' not found."
            )

        # ---------------------------------------------------------
        # Click first matching chat
        # ---------------------------------------------------------

        chat.first.click()

        # ---------------------------------------------------------
        # Wait for conversation header
        # ---------------------------------------------------------

        try:

            header = self.page.get_by_test_id(
                "conversation-header"
            )

            header.wait_for(
                timeout=15000
            )

            header_text = header.inner_text()

            print(
                f"Opened Chat : {header_text}"
            )

        except Exception:

            print(
                f"Opened chat : {search_name}"
            )

    # =============================================================
    # GET SEARCH BOX
    # =============================================================

    def _get_search_box(self):

        """
        Find the WhatsApp search textbox.

        WhatsApp changes its DOM occasionally, so several selectors
        are tried.
        """

        selectors = [

            '[data-testid="chat-list-search"]',

            '[data-testid="search"]',

            'div[role="textbox"]',

            '[contenteditable="true"]',

        ]

        for selector in selectors:

            try:

                locator = self.page.locator(
                    selector
                )

                count = locator.count()

                if count == 0:
                    continue

                for i in range(count):

                    element = locator.nth(i)

                    if element.is_visible():

                        return element

            except Exception:

                continue

        # ---------------------------------------------------------
        # Fallback
        # ---------------------------------------------------------

        try:

            textboxes = self.page.get_by_role(
                "textbox"
            )

            count = textboxes.count()

            for i in range(count):

                element = textboxes.nth(i)

                if element.is_visible():

                    return element

        except Exception:

            pass

        return None

    # =============================================================
    # SEND MESSAGE
    # =============================================================

    def send_message(self, message):

        """
        Send a text message to the currently opened chat.
        """

        if not self.page:

            raise Exception(
                "WhatsApp browser is not started."
            )

        print("Sending WhatsApp message...")

        # ---------------------------------------------------------
        # Find message textbox
        # ---------------------------------------------------------

        message_box = self.page.locator(
            '[contenteditable="true"]'
        ).last

        try:

            message_box.wait_for(
                state="visible",
                timeout=15000
            )

        except Exception:

            raise Exception(
                "WhatsApp message textbox "
                "was not found."
            )

        # ---------------------------------------------------------
        # Enter message
        # ---------------------------------------------------------

        message_box.click()

        message_box.fill(message)

        # ---------------------------------------------------------
        # Send
        # ---------------------------------------------------------

        message_box.press("Enter")

        print(
            "WhatsApp message sent successfully."
        )

    # =============================================================
    # SEND IMAGE
    # =============================================================

    def send_image(self, image_path):

        """
        Send an image to the currently opened chat.

        The actual upload logic is handled by:

            src.whatsapp_upload.upload_images
        """

        if not self.page:

            raise Exception(
                "WhatsApp browser is not started."
            )

        if not os.path.exists(image_path):

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        print(
            f"Sending image: {image_path}"
        )

        try:

            upload_images(
                self.page,
                [image_path]
            )

            print(
                f"Image sent successfully: "
                f"{image_path}"
            )

        except Exception as e:

            print(
                f"Failed to send image "
                f"{image_path}: {e}"
            )

            raise

    # =============================================================
    # SEND MULTIPLE IMAGES
    # =============================================================

    def send_images(self, image_paths):

        """
        Send multiple images to the currently opened chat.
        """

        if not image_paths:

            print(
                "No images to send."
            )

            return

        valid_images = []

        for image_path in image_paths:

            if os.path.exists(image_path):

                valid_images.append(
                    image_path
                )

            else:

                print(
                    f"Skipping missing image: "
                    f"{image_path}"
                )

        if not valid_images:

            print(
                "No valid images available."
            )

            return

        print(
            f"Sending {len(valid_images)} image(s)..."
        )

        try:

            upload_images(
                self.page,
                valid_images
            )

            print(
                "All images sent successfully."
            )

        except Exception as e:

            print(
                f"Failed to send images: {e}"
            )

            raise

    # =============================================================
    # CLOSE WHATSAPP
    # =============================================================

    def close(self):

        """
        Close the browser and stop Playwright.

        This method is safe to call even if the browser has already
        crashed or closed.
        """

        print("=" * 70)
        print("Closing WhatsApp...")
        print("=" * 70)

        # ---------------------------------------------------------
        # Close browser context
        # ---------------------------------------------------------

        try:

            if self.context:

                self.context.close()

        except Exception as e:

            print(
                f"Context close warning: {e}"
            )

        # ---------------------------------------------------------
        # Stop Playwright
        # ---------------------------------------------------------

        try:

            if self.playwright:

                self.playwright.stop()

        except Exception as e:

            print(
                f"Playwright stop warning: {e}"
            )

        # ---------------------------------------------------------
        # Clear references
        # ---------------------------------------------------------

        self.page = None
        self.context = None
        self.playwright = None

        print(
            "WhatsApp browser closed."
        )
