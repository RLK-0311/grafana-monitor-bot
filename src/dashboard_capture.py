import re
import os
import yaml

from loguru import logger
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


class DashboardCapture:
    """
    Handles Grafana dashboard navigation, authentication,
    dashboard loading, and screenshot capture.
    """

    def __init__(self, page, settings):
        self.page = page
        self.settings = settings

        # ==========================================================
        # Load Grafana Configuration
        # ==========================================================

        with open("config/grafana.yaml", "r") as f:
            self.grafana = yaml.safe_load(f)

        self.base_url = self.grafana["url"]
        self.username = self.grafana["username"]
        self.password = self.grafana["password"]

        self.login_timeout = self.grafana.get(
            "login_timeout",
            30000
        )

    # ==============================================================
    # Safe Filename
    # ==============================================================

    def safe_filename(self, name: str) -> str:
        """
        Convert dashboard name into a filesystem-safe filename.

        Example:

            CRM-80%(CFU/ARS/REF)

        becomes:

            CRM-80_CFU_ARS_REF
        """

        filename = re.sub(
            r"[^A-Za-z0-9._-]",
            "_",
            name
        )

        filename = re.sub(
            r"_+",
            "_",
            filename
        )

        return filename.strip("_")

    # ==============================================================
    # Detect Grafana Login Page
    # ==============================================================

    async def is_login_page(self):
        """
        Determine whether the current page is actually showing
        the Grafana login form.

        We do not rely only on '/login' appearing in the URL because
        Grafana authentication redirects can behave differently.
        """

        try:
            current_url = self.page.url.lower()

            # ------------------------------------------------------
            # URL Check
            # ------------------------------------------------------

            if "/login" in current_url:
                return True

            # ------------------------------------------------------
            # Username Field Check
            # ------------------------------------------------------

            username_input = self.page.locator(
                'input[name="user"]'
            )

            if await username_input.count() > 0:
                if await username_input.first.is_visible():
                    return True

            # ------------------------------------------------------
            # Password Field Check
            # ------------------------------------------------------

            password_input = self.page.locator(
                'input[name="password"]'
            )

            if await password_input.count() > 0:
                if await password_input.first.is_visible():
                    return True

            # ------------------------------------------------------
            # Sign In Button Check
            # ------------------------------------------------------

            sign_in_button = self.page.get_by_role(
                "button",
                name=re.compile(
                    r"sign\s*in",
                    re.IGNORECASE
                )
            )

            if await sign_in_button.count() > 0:
                if await sign_in_button.first.is_visible():
                    return True

        except Exception as e:

            logger.debug(
                f"Login page detection check failed: {e}"
            )

        return False

    # ==============================================================
    # Verify Successful Login
    # ==============================================================

    async def verify_login(self):
        """
        Verify that Grafana authentication actually succeeded.

        Login is considered successful when:

        1. We are no longer on the login page.
        2. The Grafana login form is no longer visible.
        """

        try:

            # ------------------------------------------------------
            # Wait briefly for redirect/navigation
            # ------------------------------------------------------

            try:

                await self.page.wait_for_load_state(
                    "domcontentloaded",
                    timeout=self.login_timeout
                )

            except PlaywrightTimeoutError:

                logger.warning(
                    "Grafana did not finish navigation within "
                    f"{self.login_timeout} ms."
                )

            # ------------------------------------------------------
            # Give Grafana time to complete authentication
            # ------------------------------------------------------

            await self.page.wait_for_timeout(3000)

            # ------------------------------------------------------
            # Check login page again
            # ------------------------------------------------------

            still_login = await self.is_login_page()

            if still_login:

                logger.error(
                    "Grafana login verification failed."
                )

                logger.error(
                    f"Current URL: {self.page.url}"
                )

                return False

            # ------------------------------------------------------
            # Login succeeded
            # ------------------------------------------------------

            logger.success(
                "Grafana login verified successfully."
            )

            logger.info(
                f"Grafana URL after login: {self.page.url}"
            )

            return True

        except Exception as e:

            logger.exception(
                f"Grafana login verification failed: {e}"
            )

            return False

    # ==============================================================
    # Grafana Login
    # ==============================================================

    async def login_if_required(self):
        """
        Automatically log into Grafana whenever the login page
        is detected.

        The method does not simply assume that clicking Sign in
        succeeded. It verifies the resulting page afterward.
        """

        # ----------------------------------------------------------
        # Check whether login is required
        # ----------------------------------------------------------

        login_required = await self.is_login_page()

        if not login_required:

            logger.info(
                "Grafana login not required. Existing session is valid."
            )

            return True

        logger.warning(
            "Grafana login page detected."
        )

        logger.info(
            "Attempting automatic Grafana login..."
        )

        # ==========================================================
        # Username
        # ==========================================================

        username_input = self.page.locator(
            'input[name="user"]'
        )

        try:

            await username_input.first.wait_for(
                state="visible",
                timeout=self.login_timeout
            )

            await username_input.first.fill(
                self.username
            )

        except Exception as e:

            logger.error(
                f"Unable to locate/fill Grafana username field: {e}"
            )

            return False

        # ==========================================================
        # Password
        # ==========================================================

        password_input = self.page.locator(
            'input[name="password"]'
        )

        try:

            await password_input.first.wait_for(
                state="visible",
                timeout=self.login_timeout
            )

            await password_input.first.fill(
                self.password
            )

        except Exception as e:

            logger.error(
                f"Unable to locate/fill Grafana password field: {e}"
            )

            return False

        # ==========================================================
        # Sign In Button
        # ==========================================================

        sign_in_button = self.page.get_by_role(
            "button",
            name=re.compile(
                r"sign\s*in",
                re.IGNORECASE
            )
        )

        # ----------------------------------------------------------
        # Fallback for Grafana versions where role/name detection
        # may not work
        # ----------------------------------------------------------

        if await sign_in_button.count() == 0:

            sign_in_button = self.page.locator(
                'button[type="submit"]'
            )

        try:

            await sign_in_button.first.wait_for(
                state="visible",
                timeout=self.login_timeout
            )

        except Exception as e:

            logger.error(
                f"Grafana Sign in button not found: {e}"
            )

            return False

        # ==========================================================
        # Click Sign In
        # ==========================================================

        logger.info(
            "Submitting Grafana login..."
        )

        try:

            await sign_in_button.first.click()

        except Exception as e:

            logger.error(
                f"Failed to click Grafana Sign in button: {e}"
            )

            return False

        # ==========================================================
        # Verify Login
        # ==========================================================

        login_success = await self.verify_login()

        if not login_success:

            logger.error(
                "Grafana automatic login FAILED."
            )

            logger.error(
                "The dashboard will not be treated as authenticated."
            )

            return False

        return True

    # ==============================================================
    # Capture Dashboard
    # ==============================================================

    async def capture_dashboard(self, dashboard):

        name = dashboard["name"]
        url = dashboard["url"]

        logger.info(
            f"Opening Dashboard : {name}"
        )

        try:

            # ======================================================
            # Open Dashboard
            # ======================================================

            await self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=120000
            )

            logger.info(
                f"Dashboard URL opened: {self.page.url}"
            )

            # ======================================================
            # Auto Login
            # ======================================================

            login_success = await self.login_if_required()

            if not login_success:

                logger.error(
                    f"Unable to authenticate to Grafana "
                    f"for dashboard: {name}"
                )

                return None

            # ======================================================
            # Wait for Dashboard Navigation
            # ======================================================

            try:

                await self.page.wait_for_load_state(
                    "networkidle",
                    timeout=120000
                )

            except PlaywrightTimeoutError:

                logger.warning(
                    f"Network did not become idle for '{name}'. "
                    "Continuing with dashboard capture."
                )

            # ======================================================
            # Final Authentication Check
            # ======================================================

            if await self.is_login_page():

                logger.error(
                    f"Grafana login page is still displayed "
                    f"for dashboard '{name}'."
                )

                return None

            # ======================================================
            # Dashboard Loaded
            # ======================================================

            logger.success(
                f"Dashboard Loaded : {name}"
            )

            # ======================================================
            # Wait for Panels
            # ======================================================

            wait_after_load = self.settings[
                "capture"
            ].get(
                "wait_after_load",
                5
            )

            logger.info(
                f"Waiting {wait_after_load} seconds "
                "for Grafana panels..."
            )

            await self.page.wait_for_timeout(
                wait_after_load * 1000
            )

            # ======================================================
            # Screenshot Filename
            # ======================================================

            filename = self.safe_filename(
                name
            )

            output_file = (
                f"screenshots/{filename}.png"
            )

            # ======================================================
            # Ensure Screenshot Directory Exists
            # ======================================================

            os.makedirs(
                "screenshots",
                exist_ok=True
            )

            # ======================================================
            # Capture Screenshot
            # ======================================================

            logger.info(
                f"Capturing screenshot : {output_file}"
            )

            await self.page.screenshot(
                path=output_file,
                full_page=self.settings[
                    "capture"
                ].get(
                    "full_page",
                    True
                )
            )

            # ======================================================
            # Screenshot Saved
            # ======================================================

            logger.success(
                f"Screenshot Saved : {output_file}"
            )

            return output_file

        except Exception:

            logger.exception(
                f"Failed to capture '{name}'"
            )

            return None
