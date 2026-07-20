import asyncio
import re

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

    # First graph panel
    graph = page.locator(".graph-panel").first

    box = await graph.bounding_box()

    print(box)

    # Move mouse to the center of the graph
    await page.mouse.move(
        box["x"] + box["width"] / 2,
        box["y"] + box["height"] / 2
    )

    await page.wait_for_timeout(1000)

    values = await page.locator(".graph-tooltip-value").all_inner_texts()

    print("\nTooltip values")
    print("----------------")

    numbers = []

    for value in values:

        print(value)

        m = re.search(r"(\d+(\.\d+)?)", value)

        if m:
            numbers.append(float(m.group(1)))

    print("\nNumbers =", numbers)

    if numbers:
        print("Maximum =", max(numbers))
    else:
        print("No values found.")

    input("\nPress ENTER to exit...")

    await browser.stop()


asyncio.run(main())
