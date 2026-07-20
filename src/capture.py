from pathlib import Path
from datetime import datetime
import yaml

from playwright.sync_api import sync_playwright

PROFILE_PATH = "browser/profile"
SCREENSHOT_DIR = "screenshots"

# Create screenshot directory if it doesn't exist
Path(SCREENSHOT_DIR).mkdir(exist_ok=True)

# Read dashboards
with open("config/dashboards.yaml", "r") as file:
    config = yaml.safe_load(file)

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        headless=False,
        viewport={"width": 1920, "height": 1080},
    )

    for dashboard in config["dashboards"]:

        print(f"\nOpening : {dashboard['name']}")

        page = context.new_page()

        page.goto(
            dashboard["url"],
            wait_until="networkidle",
            timeout=120000,
        )

        # Wait for Grafana graphs
        page.wait_for_timeout(5000)

        # Refresh once
        page.reload(wait_until="networkidle")

        page.wait_for_timeout(3000)

        filename = (
            datetime.now().strftime("%Y%m%d_%H%M%S")
            + "_"
            + dashboard["name"].replace(" ", "_")
            + ".png"
        )

        path = f"{SCREENSHOT_DIR}/{filename}"

        page.screenshot(
            path=path,
            full_page=True,
        )

        print(f"Saved : {filename}")

        page.close()

    context.close()

print("\nAll screenshots completed.")