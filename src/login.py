from playwright.sync_api import sync_playwright

PROFILE_PATH = "browser/profile"

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_PATH,
        headless=False
    )

    page = context.new_page()

    page.goto("https://monitoring.creditmantri.com/d/vL8ASiO7k/cm-rds-alert-85?orgId=1&refresh=5s&from=now-30m&to=now")

    print("=" * 60)
    print("LOGIN TO GRAFANA MANUALLY")
    print("DO NOT CLOSE THE BROWSER")
    print("After login, press ENTER in the terminal.")
    print("=" * 60)

    input()

    context.close()