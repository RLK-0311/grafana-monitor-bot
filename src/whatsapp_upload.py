import time


def upload_images(page, image_paths):

    print("Opening attachment flow...")

    # Give WhatsApp time to stabilize
    page.wait_for_timeout(1200)

    photos_menu_opened = False

    # ==========================================================
    # Open Attach -> Photos & videos
    # ==========================================================

    for attempt in range(2):

        try:

            attach = page.get_by_role(
                "button",
                name="Attach"
            )

            if attach.count() > 0:

                attach.first.click(force=True)

                page.wait_for_timeout(1500)

        except Exception:

            print(
                f"Attach click failed (attempt {attempt + 1})"
            )

        try:

            photos_option = page.get_by_text(
                "Photos & videos",
                exact=True
            )

            photos_option.wait_for(timeout=5000)

            photos_option.click()

            page.wait_for_timeout(2000)

            photos_menu_opened = True

            break

        except Exception:

            print(
                f"Could not click Photos & videos "
                f"(attempt {attempt + 1})"
            )

    if not photos_menu_opened:

        raise Exception(
            "Unable to open Photos & videos menu."
        )

    # ==========================================================
    # Locate Photos & Videos input
    # ==========================================================

    print("=" * 60)
    print("Available file inputs")
    print("=" * 60)

    inputs = page.locator("input[type=file]")

    count = inputs.count()

    print(f"Total file inputs: {count}")

    photo_input = None

    for i in range(count):

        inp = inputs.nth(i)

        accept = (inp.get_attribute("accept") or "").lower()

        multiple = inp.get_attribute("multiple")

        print(
            f"{i} accept={accept} multiple={multiple}"
        )

        # Skip Sticker input
        if accept == "image/*":
            continue

        # Photos & Videos input
        if "video" in accept:

            photo_input = inp

            break

    if photo_input is None:

        raise Exception(
            "Photos & Videos input not found."
        )

    # ==========================================================
    # Upload Album
    # ==========================================================

    print(f"Uploading {len(image_paths)} images...")

    photo_input.set_input_files(image_paths)

    # Give WhatsApp time to create preview
    page.wait_for_timeout(5000)


    # ==========================================================
    # Wait for Send button
    # ==========================================================

    print("Waiting for Send button...")

    send_button = page.get_by_role(
        "button",
        name="Send"
    )

    deadline = time.time() + 30

    final_btn = None
    selected_index = -1

    while time.time() < deadline:

        try:

            total = send_button.count()

            for idx in range(total):

                btn = send_button.nth(idx)

                if btn.is_visible():

                    final_btn = btn
                    selected_index = idx

                    break

            if final_btn:

                break

        except Exception:

            pass

        page.wait_for_timeout(500)

    if final_btn is None:

        page.screenshot(
            path="send_button_not_found.png",
            full_page=True
        )

        raise Exception(
            "Send button not found after upload."
        )

    
    # ==========================================================
    # Send Album
    # ==========================================================

    print("Sending image album...")

    print("=" * 60)
    print(f"Total Send Buttons Found : {send_button.count()}")
    print(f"Clicking Send Button Index : {selected_index}")
    print("=" * 60)

    page.screenshot(
        path="before_send.png",
        full_page=True
    )

    # Click normally (avoid force=True for this test)
    final_btn.click()

    print("Waiting 60 seconds... DO NOT CLOSE THE BROWSER")

    # Give WhatsApp plenty of time to upload all mediale
    page.wait_for_timeout(60000)

    page.screenshot(
        path="after_60_seconds.png",
        full_page=True
    )

    print("Finished waiting.")

    print("=" * 60)
    print("Checking whether album preview still exists...")
    print("=" * 60)

    preview = page.locator("div[aria-label='Media preview']")

    try:
        if preview.count() > 0 and preview.first.is_visible():
            print("Album preview is STILL OPEN.")
        else:
            print("Album preview CLOSED.")
    except Exception:
        print("Album preview CLOSED.")

    print("Album upload finished.")