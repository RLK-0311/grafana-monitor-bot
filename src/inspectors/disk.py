from loguru import logger


class DiskInspector:

    def __init__(self, threshold):
        self.threshold = threshold

    def check(self, value):

        logger.info(f"Disk = {value}%")

        if value >= self.threshold:
            return {
                "status": "CRITICAL",
                "metric": "DISK",
                "value": value,
                "threshold": self.threshold
            }

        return None