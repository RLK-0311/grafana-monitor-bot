import asyncio

from src.browser_manager import BrowserManager
from src.config_loader import ConfigLoader


config = ConfigLoader().load_all()


async def main():

    browser = BrowserManager(config["settings"])
    page = await browser.start()

    dashboard = config["dashboards"]["dashboards"][3]   # Change index if needed

    await page.goto(
        dashboard["url"],
        wait_until="domcontentloaded",
        timeout=60000
    )

    await page.wait_for_timeout(5000)

    panel = page.locator(".graph-panel").first

    box = await panel.bounding_box()

    print(box)

    await page.mouse.move(
        box["x"] + box["width"] * 0.98,
        box["y"] + box["height"] * 0.50
    )

    await page.wait_for_timeout(2000)

    html = await page.content()

    with open("tooltip_page.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Saved tooltip_page.html")

    input("Keep browser open. Press ENTER...")

    await browser.stop()


asyncio.run(main())
