from pathlib import Path
from loguru import logger


async def capture_panel(page, panel_title: str, output_file: str) -> bool:
    """
    Capture a Grafana panel screenshot by its title.

    Args:
        page: Playwright page object
        panel_title: Panel title (e.g. CPU Busy)
        output_file: Output screenshot path

    Returns:
        True if successful, False otherwise
    """

    try:
        logger.info(f"Capturing panel: {panel_title}")

        # Wait until dashboard is fully loaded
        await page.wait_for_load_state("networkidle")

        # Locate panel title
        title = page.locator(f"text={panel_title}").first

        # Wait until title is visible
        await title.wait_for(timeout=10000)

        # Find the panel container
        panel = title.locator(
            "xpath=ancestor::div[contains(@class,'panel-container')]"
        ).first

        # Scroll into view
        await panel.scroll_into_view_if_needed()

        # Allow charts to finish rendering
        await page.wait_for_timeout(1500)

        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # Capture screenshot
        await panel.screenshot(path=output_file)

        logger.success(f"Screenshot saved: {output_file}")

        return True

    except Exception as e:
        logger.error(f"Failed to capture panel '{panel_title}': {e}")
        return False