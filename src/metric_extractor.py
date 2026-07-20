import re
from loguru import logger


class MetricExtractor:
    """
    Extract Grafana panel values.

    For graph panels:
        Hover over the graph and read the tooltip values.

    For stat panels:
        Fall back to panel text.

    Returns:

    {
        "raw_text": "...",
        "panels": {
            "CPU Busy": 26.5,
            "RAM Used": 61.8,
            ...
        }
    }
    """

    def __init__(self, page):
        self.page = page

    async def _get_graph_value(self, index):
        """
        Hover over a graph panel and return the maximum value shown
        in the Grafana tooltip.
        """

        try:

            graph = self.page.locator(".graph-panel").nth(index)

            if await graph.count() == 0:
                return None

            box = await graph.bounding_box()

            if not box:
                return None

            # Hover in the middle of the graph
            await self.page.mouse.move(
                box["x"] + box["width"] / 2,
                box["y"] + box["height"] / 2
            )

            await self.page.wait_for_timeout(500)

            values = await self.page.locator(
                ".graph-tooltip-value"
            ).all_inner_texts()

            numbers = []

            for value in values:

                m = re.search(r"(\d+(?:\.\d+)?)", value)

                if m:
                    numbers.append(float(m.group()))

            if numbers:

                logger.success(
                    f"Tooltip Values : {numbers}"
                )

                logger.success(
                    f"Maximum Tooltip Value : {max(numbers)}"
                )

                return max(numbers)

            return None

        except Exception as e:

            logger.debug(f"Tooltip extraction failed : {e}")

            return None

    async def extract_metrics(self):

        metrics = {
            "raw_text": "",
            "panels": {}
        }

        try:

            title_locator = self.page.locator(".panel-title")
            panel_locator = self.page.locator(".panel-content")

            title_count = await title_locator.count()
            panel_count = await panel_locator.count()

            logger.info(f"Panel Titles Found : {title_count}")
            logger.info(f"Panel Contents Found : {panel_count}")

            count = min(title_count, panel_count)

            for i in range(count):

                try:

                    title = (
                        await title_locator
                        .nth(i)
                        .inner_text()
                    ).strip()

                except Exception:

                    title = f"Panel_{i}"

                try:

                    content = (
                        await panel_locator
                        .nth(i)
                        .inner_text()
                    ).strip()

                except Exception:

                    content = ""

                # ------------------------------------------
                # Try reading the graph tooltip
                # ------------------------------------------

                graph_value = await self._get_graph_value(i)

                if graph_value is not None:

                    logger.success(
                        f"{title} -> Using Tooltip Value : {graph_value}"
                    )

                    metrics["panels"][title] = graph_value

                else:

                    metrics["panels"][title] = content

                await self.page.wait_for_timeout(150)

            metrics["raw_text"] = "\n".join(
                map(str, metrics["panels"].values())
            )

            logger.info("=" * 80)
            logger.info("Extracted Panels")
            logger.info("=" * 80)

            for title, content in metrics["panels"].items():

                logger.info(f"{title} --> {content}")

            logger.info("=" * 80)

        except Exception as e:

            logger.exception(e)

        return metrics
