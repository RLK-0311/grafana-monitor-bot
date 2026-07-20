import asyncio

from src.browser_manager import BrowserManager
from src.config_loader import ConfigLoader

config = ConfigLoader().load_all()


async def main():

    browser = BrowserManager(config["settings"])
    page = await browser.start()

    dashboard = config["dashboards"]["dashboards"][2]

    await page.goto(
        dashboard["url"],
        wait_until="domcontentloaded",
        timeout=60000
    )

    await page.wait_for_timeout(5000)

    panel = page.locator(".panel-content").first

    print(await panel.inner_html())

    await browser.stop()


asyncio.run(main())
