import re
from pathlib import Path

import yaml
from loguru import logger


class DashboardCapture:
    def __init__(self, page, settings):
        self.page = page
        self.settings = settings

        # Create screenshots directory
        Path("screenshots").mkdir(parents=True, exist_ok=True)

        # Load Grafana credentials
        with open("config/grafana.yaml", "r") as f:
            self.grafana = yaml.safe_load(f)

        self.base_url = self.grafana["url"]
        self.username = self.grafana["username"]
        self.password = self.grafana["password"]

    def safe_filename(self, name: str) -> str:
        """
        Convert dashboard name into a safe filename.

        Example:
            CRM-80%(CFU/ARS/REF)

        becomes

            CRM-80_CFU_ARS_REF
        """

        filename = re.sub(r"[^A-Za-z0-9._-]", "_", name)
        filename = re.sub(r"_+", "_", filename)

        return filename.strip("_")

    async def login_if_required(self):
        """
        Automatically logs into Grafana whenever
        the login page appears.
        """

        current_url = self.page.url.lower()

        if "/login" not in current_url:
            return

        logger.warning("Grafana login page detected.")

        await self.page.fill(
            'input[name="user"]',
            self.username
        )

        await self.page.fill(
            'input[name="password"]',
            self.password
        )

        await self.page.click(
            'button[type="submit"]'
        )

        await self.page.wait_for_load_state("networkidle")

        logger.success("Grafana login successful.")

    async def capture_dashboard(self, dashboard):

        name = dashboard["name"]
        url = dashboard["url"]

        logger.info(f"Opening Dashboard : {name}")

        try:

            ############################################################
            # Open Dashboard
            ############################################################

            await self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=120000
            )

            ############################################################
            # Auto Login
            ############################################################

            await self.login_if_required()

            ############################################################
            # Wait for Dashboard
            ############################################################

            await self.page.wait_for_load_state("networkidle")

            logger.success("Dashboard Loaded")

            ############################################################
            # Wait for Panels
            ############################################################

            await self.page.wait_for_timeout(
                self.settings["capture"]["wait_after_load"] * 1000
            )

            ############################################################
            # Screenshot Filename
            ############################################################

            filename = self.safe_filename(name)

            output_file = f"screenshots/{filename}.png"

            ############################################################
            # Capture Screenshot
            ############################################################

            await self.page.screenshot(
                path=output_file,
                full_page=self.settings["capture"]["full_page"]
            )

            logger.success(
                f"Screenshot Saved : {output_file}"
            )

            return output_file

        except Exception:

            logger.exception(
                f"Failed to capture '{name}'"
            )

            return None
