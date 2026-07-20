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

    input("Open your WhatsApp chat and press ENTER...")

    print("\nClick the ATTACH (+) button yourself, then press ENTER...")
    input()

    print("\nButtons after clicking Attach:\n")

    buttons = page.get_by_role("button")

    for i in range(buttons.count()):
        try:
            b = buttons.nth(i)
            print(
                i,
                "aria-label =", b.get_attribute("aria-label"),
                "| text =", b.inner_text()
            )
        except Exception:
            pass

    print("\nFile Inputs\n")

    inputs = page.locator("input[type=file]")

    print("Total:", inputs.count())

    for i in range(inputs.count()):
        inp = inputs.nth(i)
        print(
            i,
            "accept =", inp.get_attribute("accept"),
            "| multiple =", inp.get_attribute("multiple")
        )

    input("\nPress ENTER to exit...")

    context.close()
