from loguru import logger


class RDSInspector:

    def __init__(self, warning, critical):
        self.warning = warning
        self.critical = critical

    def check(self, value):

        logger.info(f"RDS = {value}%")

        if value >= self.critical:
            return {
                "status": "CRITICAL",
                "metric": "RDS",
                "value": value,
                "threshold": self.critical
            }

        if value >= self.warning:
            return {
                "status": "WARNING",
                "metric": "RDS",
                "value": value,
                "threshold": self.warning
            }

        return None