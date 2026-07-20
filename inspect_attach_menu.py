from playwright.sync_api import sync_playwright

PROFILE = "browser/whatsapp_profile"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE,
        headless=False,
        no_viewport=True,
        viewport=None,
        args=["--start-maximized"],
    )
    page = context.pages[0] if context.pages else context.new_page()
    page.goto("https://web.whatsapp.com")

    input("Open your 'SonJIO (You)' chat, then press ENTER here...")

    attach_button = page.get_by_role("button", name="Attach")
    attach_button.wait_for(timeout=10000)
    attach_button.click()

    page.wait_for_timeout(1000)

    print("\n--- Buttons visible after clicking Attach ---")
    buttons = page.locator("button, div[role='button']").all()
    for i, btn in enumerate(buttons):
        if not btn.is_visible():
            continue
        aria = btn.get_attribute("aria-label")
        title = btn.get_attribute("title")
        text = btn.inner_text().strip()
        if aria or title or text:
            print(f"[{i}] aria-label={aria!r} title={title!r} text={text!r}")

    print("\n--- File inputs currently in DOM ---")
    inputs = page.locator('input[type="file"]').all()
    for i, inp in enumerate(inputs):
        print(f"[{i}] accept={inp.get_attribute('accept')!r}")

    input("\nPress ENTER to close the browser...")
    context.close()
