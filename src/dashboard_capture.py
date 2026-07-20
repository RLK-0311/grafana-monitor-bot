import re
from pathlib import Path
from loguru import logger
class DashboardCapture:
    def __init__(self, page, settings):
        self.page = page
        self.settings = settings
        # Create screenshots directory if it doesn't exist
        Path("screenshots").mkdir(parents=True, exist_ok=True)
    def safe_filename(self, name: str) -> str:
        """
        Convert dashboard name into a safe filename.
        Example:
        CRM-80%(CFU/ARS/REF)
        ->
        CRM-80__CFU_ARS_REF_
        """
        filename = re.sub(r"[^A-Za-z0-9._-]", "_", name)
        # Remove duplicate underscores
        filename = re.sub(r"_+", "_", filename)
        return filename.strip("_")
    async def capture_dashboard(self, dashboard):
        name = dashboard["name"]
        url = dashboard["url"]
        logger.info(f"Opening Dashboard : {name}")
        try:
            # --------------------------------------------------------
            # Open Dashboard
            # --------------------------------------------------------
            await self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=120000
            )
            logger.success("Dashboard Loaded")

            # Give Grafana a few seconds to finish rendering panels
            await self.page.wait_for_timeout(
                self.settings["capture"]["wait_after_load"] * 1000
            )
            # --------------------------------------------------------
            # Safe Screenshot Filename
            # --------------------------------------------------------
            filename = self.safe_filename(name)
            output_file = f"screenshots/{filename}.png"
            # --------------------------------------------------------
            # Capture Screenshot
            # --------------------------------------------------------
            await self.page.screenshot(
                path=output_file,
                full_page=self.settings["capture"]["full_page"]
            )
            logger.success(f"Screenshot Saved : {output_file}")

            return output_file

        except Exception as e:
            logger.exception(f"Failed to capture '{name}'")

            return None
