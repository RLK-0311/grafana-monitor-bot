import asyncio
from playwright.async_api import async_playwright

from utils.screenshot import capture_panel

# Replace this with your actual Grafana dashboard URL
DASHBOARD_URL = "https://monitoring.creditmantri.com/d/CM-CRON/cm-cron-90?orgId=1&refresh=30s&from=now-30m&to=now"

PROFILE_PATH = "browser/profile"


async def main():
    async with async_playwright() as p:

        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_PATH,
            headless=False,
            viewport={"width": 1920, "height": 1080},
        )

        page = await context.new_page()

        print("Opening dashboard...")

        await page.goto(
            DASHBOARD_URL,
            wait_until="networkidle",
            timeout=120000,
        )

        # Give Grafana a little extra time
        await page.wait_for_timeout(3000)

        success = await capture_panel(
            page=page,
            panel_title="CPU Busy",
            output_file="screenshots/cpu_busy.png",
        )

        if success:
            print("✅ Panel screenshot captured successfully.")
        else:
            print("❌ Failed to capture panel.")

        print("Browser will stay open for 10 seconds...")
        await page.wait_for_timeout(10000)

        await context.close()


if __name__ == "__main__":
    asyncio.run(main())