import asyncio

from src.config_loader import ConfigLoader
from src.browser_manager import BrowserManager


config = ConfigLoader().load_all()


async def main():

    browser = BrowserManager(config["settings"])
    page = await browser.start()

    dashboard = config["dashboards"]["dashboards"][2]   # AZURE-WAREHOUSE

    await page.goto(
        dashboard["url"],
        wait_until="domcontentloaded",
        timeout=60000,
    )

    await page.wait_for_timeout(5000)

    panels = page.locator(".panel-content")

    count = await panels.count()

    print("=" * 100)
    print("TOTAL PANELS :", count)
    print("=" * 100)

    for i in range(count):

        print("\n")
        print("=" * 100)
        print(f"PANEL {i}")
        print("=" * 100)

        try:
            text = await panels.nth(i).inner_text()

            print("\nTEXT:\n")
            print(text)

        except Exception as e:
            print(e)

        try:
            html = await panels.nth(i).inner_html()

            print("\nHTML:\n")
            print(html[:5000])

        except Exception as e:
            print(e)

    await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())
