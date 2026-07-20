import asyncio

from src.config_loader import ConfigLoader
from src.browser_manager import BrowserManager
from src.kafka_extractor import KafkaExtractor


async def main():

    # Load config
    config = ConfigLoader().load_all()

    # Start browser
    browser = BrowserManager(config["settings"])
    page = await browser.start()

    # Open Kafka UI
    await page.goto(
        "https://kafka-cdc.creditmantri.com/ui/clusters/local/consumer-groups?sortBy=STATE&sortDirection=desc",
        wait_until="networkidle"
    )

    # Give the table time to render
    await page.wait_for_timeout(3000)

    extractor = KafkaExtractor(page)

    result = await extractor.extract()

    print("\n=============================")
    print(result)
    print("=============================\n")

    input("Press ENTER to exit...")

    await browser.stop()


asyncio.run(main())
