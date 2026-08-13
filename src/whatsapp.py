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

        The persistent profile stores the WhatsApp Web login session.

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
        # Get existing page or create new page
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

            print(
                f"WhatsApp navigation warning: {e}"
            )

        print("Waiting for WhatsApp to load...")

        # ---------------------------------------------------------
        # Wait for WhatsApp readiness
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

        Several selectors are checked because WhatsApp Web's DOM
        can change.
        """

        timeout_seconds = 120

        start_time = time.time()

        print(
            f"Waiting up to {timeout_seconds} seconds "
            "for WhatsApp..."
        )

        last_status = None

        while time.time() - start_time < timeout_seconds:

            try:

                # -------------------------------------------------
                # Check page state
                # -------------------------------------------------

                if self.page is None:

                    print(
                        "WhatsApp page object is not available."
                    )

                    return False

                if self.page.is_closed():

                    print(
                        "WhatsApp page was closed."
                    )

                    return False

                # -------------------------------------------------
                # Current URL
                # -------------------------------------------------

                current_url = self.page.url

                if current_url != last_status:

                    print(
                        f"WhatsApp URL: {current_url}"
                    )

                    last_status = current_url

                # -------------------------------------------------
                # Check role=textbox
                # -------------------------------------------------

                textboxes = self.page.get_by_role(
                    "textbox"
                )

                try:

                    textbox_count = textboxes.count()

                except Exception:

                    textbox_count = 0

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
                # Check common WhatsApp selectors
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

                        if count == 0:
                            continue

                        for i in range(count):

                            try:

                                element = locator.nth(i)

                                if element.is_visible():

                                    print(
                                        "WhatsApp ready using "
                                        f"selector: {selector}"
                                    )

                                    return True

                            except Exception:

                                continue

                    except Exception:

                        continue

                # -------------------------------------------------
                # Detect QR/login screen
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
                        "WhatsApp login/QR screen detected."
                    )

                    print(
                        "If QR code is displayed, "
                        "scan it using your phone."
                    )

                # -------------------------------------------------
                # Detect page text
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

                    elif (
                        "Use WhatsApp on your computer"
                        in body_text
                    ):

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

            try:

                self.page.wait_for_timeout(3000)

            except Exception:

                time.sleep(3)

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
        Save a screenshot when WhatsApp fails to load or a chat
        cannot be verified.
        """

        try:

            if not self.page:
                return

            path = "debug_whatsapp_load_failed.png"

            self.page.screenshot(
                path=path,
                full_page=True
            )

            print(
                f"WhatsApp debug screenshot saved: {path}"
            )

        except Exception as e:

            print(
                "Could not save WhatsApp debug screenshot: "
                f"{e}"
            )

    # =============================================================
    # NORMALIZE CHAT NAME
    # =============================================================

    @staticmethod
    def _normalize_chat_name(name):

        """
        Normalize chat names before comparison.

        Example:

            'CM-MONITORING'
            'CM-MONITORING '

        become comparable strings.
        """

        if name is None:

            return ""

        return " ".join(
            str(name)
            .strip()
            .lower()
            .split()
        )

    # =============================================================
    # OPEN CHAT
    # =============================================================

    def open_chat(self, chat_name):

        """
        Search for and open a WhatsApp chat.

        IMPORTANT:

        After clicking the chat, this method verifies the actual
        conversation header.

        This prevents screenshots from accidentally being sent
        to the previous chat if WhatsApp fails to switch chats.
        """

        if not self.page:

            raise Exception(
                "WhatsApp browser is not started. "
                "Call start() first."
            )

        if not chat_name:

            raise Exception(
                "WhatsApp chat name is empty."
            )

        print("=" * 70)
        print(
            f"Searching WhatsApp chat: {chat_name}"
        )
        print("=" * 70)

        # ---------------------------------------------------------
        # Get search box
        # ---------------------------------------------------------

        search = self._get_search_box()

        if search is None:

            self._save_debug_screenshot()

            raise Exception(
                "WhatsApp search textbox not found."
            )

        # ---------------------------------------------------------
        # Click search box
        # ---------------------------------------------------------

        try:

            search.click()

        except Exception as e:

            self._save_debug_screenshot()

            raise Exception(
                f"Could not click WhatsApp search box: {e}"
            )

        # ---------------------------------------------------------
        # Clear existing search
        # ---------------------------------------------------------

        try:

            search.fill("")

        except Exception:

            try:

                search.press("Control+A")
                search.press("Backspace")

            except Exception as e:

                self._save_debug_screenshot()

                raise Exception(
                    f"Could not clear WhatsApp search box: {e}"
                )

        # ---------------------------------------------------------
        # Type chat name
        # ---------------------------------------------------------

        print(
            f"Typing chat name: {chat_name}"
        )

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
        # Extract actual searchable name
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

        expected_name = self._normalize_chat_name(
            search_name
        )

        print(
            f"Expected chat: {search_name}"
        )

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

            try:

                chat = self.page.get_by_text(
                    search_name,
                    exact=True
                )

                count = chat.count()

            except Exception:

                count = 0

        # ---------------------------------------------------------
        # Additional fallback
        # ---------------------------------------------------------

        if count == 0:

            try:

                chat = self.page.locator(
                    f'span[title*="{search_name}"]'
                )

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

        print(
            f"Found {count} matching chat element(s)."
        )

        # ---------------------------------------------------------
        # Click first matching chat
        # ---------------------------------------------------------

        try:

            chat.first.click()

        except Exception as e:

            self._save_debug_screenshot()

            raise Exception(
                f"Could not click chat "
                f"'{search_name}': {e}"
            )

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # Wait for WhatsApp to actually switch conversation.
        # ---------------------------------------------------------

        print(
            f"Waiting for WhatsApp to open "
            f"'{search_name}'..."
        )

        self.page.wait_for_timeout(3000)

        # ---------------------------------------------------------
        # VERIFY ACTUAL CONVERSATION
        # ---------------------------------------------------------

        verified = self._verify_open_chat(
            expected_name
        )

        if not verified:

            self._save_debug_screenshot()

            raise Exception(
                f"WhatsApp opened the wrong chat. "
                f"Expected '{search_name}'. "
                f"Screenshot/image upload has been stopped."
            )

        print(
            f"Verified correct WhatsApp chat: "
            f"{search_name}"
        )

    # =============================================================
    # VERIFY OPEN CHAT
    # =============================================================

    def _verify_open_chat(self, expected_name):

        """
        Verify that WhatsApp actually opened the requested chat.

        Returns:

            True  -> correct chat is open
            False -> wrong chat / verification failed
        """

        print(
            "Verifying active WhatsApp conversation..."
        )

        expected_name = self._normalize_chat_name(
            expected_name
        )

        # ---------------------------------------------------------
        # Try conversation header
        # ---------------------------------------------------------

        header_text = ""

        try:

            header = self.page.get_by_test_id(
                "conversation-header"
            )

            header.wait_for(
                timeout=15000
            )

            header_text = header.inner_text().strip()

        except Exception:

            # -----------------------------------------------------
            # Fallback selectors
            # -----------------------------------------------------

            fallback_selectors = [

                '[data-testid="conversation-header"]',

                'header',

            ]

            for selector in fallback_selectors:

                try:

                    locator = self.page.locator(
                        selector
                    )

                    count = locator.count()

                    if count == 0:
                        continue

                    for i in range(count):

                        try:

                            element = locator.nth(i)

                            if element.is_visible():

                                text = (
                                    element
                                    .inner_text()
                                    .strip()
                                )

                                if text:

                                    header_text = text

                                    break

                        except Exception:

                            continue

                    if header_text:
                        break

                except Exception:

                    continue

        # ---------------------------------------------------------
        # Could not determine active chat
        # ---------------------------------------------------------

        if not header_text:

            print(
                "Could not determine current "
                "WhatsApp conversation header."
            )

            return False

        # ---------------------------------------------------------
        # Log actual header
        # ---------------------------------------------------------

        print(
            f"Actual WhatsApp conversation: "
            f"{header_text}"
        )

        # ---------------------------------------------------------
        # Normalize
        # ---------------------------------------------------------

        actual_text = self._normalize_chat_name(
            header_text
        )

        # ---------------------------------------------------------
        # Direct comparison
        # ---------------------------------------------------------

        if expected_name == actual_text:

            print(
                "Chat verification successful."
            )

            return True

        # ---------------------------------------------------------
        # Header may contain additional text
        #
        # Example:
        #
        # CM-MONITORING
        # 14 participants
        #
        # ---------------------------------------------------------

        if expected_name in actual_text:

            print(
                "Chat verification successful "
                "(partial header match)."
            )

            return True

        # ---------------------------------------------------------
        # Verification failed
        # ---------------------------------------------------------

        print(
            "CHAT VERIFICATION FAILED"
        )

        print(
            f"Expected : {expected_name}"
        )

        print(
            f"Actual   : {actual_text}"
        )

        return False

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

        # ---------------------------------------------------------
        # Try known selectors
        # ---------------------------------------------------------

        for selector in selectors:

            try:

                locator = self.page.locator(
                    selector
                )

                count = locator.count()

                if count == 0:
                    continue

                for i in range(count):

                    try:

                        element = locator.nth(i)

                        if element.is_visible():

                            return element

                    except Exception:

                        continue

            except Exception:

                continue

        # ---------------------------------------------------------
        # Fallback to role textbox
        # ---------------------------------------------------------

        try:

            textboxes = self.page.get_by_role(
                "textbox"
            )

            count = textboxes.count()

            for i in range(count):

                try:

                    element = textboxes.nth(i)

                    if element.is_visible():

                        return element

                except Exception:

                    continue

        except Exception:

            pass

        return None

    # =============================================================
    # SEND MESSAGE
    # =============================================================

    def send_message(self, message):

        """
        Send a text message to the currently opened chat.

        IMPORTANT:

        The caller must first call open_chat() and verify the
        destination chat.
        """

        if not self.page:

            raise Exception(
                "WhatsApp browser is not started."
            )

        if not message:

            print(
                "No WhatsApp message to send."
            )

            return

        print(
            "Sending WhatsApp message..."
        )

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

            self._save_debug_screenshot()

            raise Exception(
                "WhatsApp message textbox "
                "was not found."
            )

        # ---------------------------------------------------------
        # Enter message
        # ---------------------------------------------------------

        try:

            message_box.click()

            message_box.fill(message)

        except Exception:

            # Fallback for contenteditable elements

            message_box.click()

            message_box.press("Control+A")

            message_box.press("Backspace")

            message_box.press_sequentially(
                message,
                delay=5
            )

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
        Send a single image to the currently opened chat.

        The actual upload logic is handled by:

            src.whatsapp_upload.upload_images
        """

        if not self.page:

            raise Exception(
                "WhatsApp browser is not started."
            )

        if not image_path:

            raise ValueError(
                "Image path is empty."
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

        IMPORTANT:

        This method assumes open_chat() has already verified the
        destination chat.

        Therefore:

            open_chat("CM-MONITORING")
                    ↓
            verification
                    ↓
            send_images()

        If open_chat() fails, this method is never reached.
        """

        if not self.page:

            raise Exception(
                "WhatsApp browser is not started."
            )

        if not image_paths:

            print(
                "No images to send."
            )

            return

        # ---------------------------------------------------------
        # Validate images
        # ---------------------------------------------------------

        valid_images = []

        for image_path in image_paths:

            if not image_path:

                continue

            if os.path.exists(image_path):

                valid_images.append(
                    image_path
                )

            else:

                print(
                    f"Skipping missing image: "
                    f"{image_path}"
                )

        # ---------------------------------------------------------
        # No valid images
        # ---------------------------------------------------------

        if not valid_images:

            print(
                "No valid images available."
            )

            return

        # ---------------------------------------------------------
        # Log upload target
        #
        # The active chat was already verified by open_chat().
        # ---------------------------------------------------------

        print("=" * 70)
        print(
            "PREPARING WHATSAPP IMAGE UPLOAD"
        )
        print("=" * 70)

        print(
            f"Images to send: {len(valid_images)}"
        )

        for image in valid_images:

            print(
                f"  - {image}"
            )

        print("=" * 70)

        # ---------------------------------------------------------
        # Upload
        # ---------------------------------------------------------

        try:

            upload_images(
                self.page,
                valid_images
            )

            print("=" * 70)
            print(
                "All images sent successfully."
            )
            print("=" * 70)

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

        Safe to call even if the browser has already crashed
        or closed.
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