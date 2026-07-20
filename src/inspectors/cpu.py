from loguru import logger


class CPUInspector:

    def __init__(self, threshold):
        self.threshold = threshold

    def check(self, value):

        logger.info(f"CPU = {value}%")

        if value >= self.threshold:
            return {
                "status": "CRITICAL",
                "metric": "CPU",
                "value": value,
                "threshold": self.threshold
            }

        return None