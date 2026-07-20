from playwright.async_api import async_playwright
from loguru import logger
import asyncio


class BrowserManager:

    def __init__(self, config):

        self.config = config
        self.playwright = None
        self.context = None
        self.page = None

    async def start(self):

        logger.info("Starting Chrome Browser...")

        self.playwright = await async_playwright().start()

        self.context = (
            await self.playwright.chromium.launch_persistent_context(
                user_data_dir="browser/profile",
                headless=self.config["browser"]["headless"],
                ignore_https_errors=True,
                viewport={
                    "width": self.config["browser"]["width"],
                    "height": self.config["browser"]["height"]
                },
                args=[
                    "--ignore-certificate-errors"
                ]
            )
        )

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = await self.context.new_page()

        logger.info(f"Pages in context : {len(self.context.pages)}")
        logger.info(f"Current page URL : {self.page.url}")

        logger.success("Chrome Browser Started Successfully")

        return self.page

    async def stop(self):

        logger.info("Closing Browser...")

        try:

            if self.page and not self.page.is_closed():
                await self.page.close()

        except Exception as e:

            logger.warning(f"Page close skipped : {e}")

        try:

            if self.context:
                await self.context.close()

        except Exception as e:

            logger.warning(f"Context close skipped : {e}")

        #
        # Give Chromium time to terminate child processes
        #
        await asyncio.sleep(2)

        try:

            if self.playwright:
                await self.playwright.stop()

        except Exception as e:

            logger.warning(f"Playwright stop skipped : {e}")

        #
        # Allow asyncio cleanup before the loop exits
        #
        await asyncio.sleep(1)

        logger.success("Browser Closed")