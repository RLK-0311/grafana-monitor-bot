from loguru import logger


class ThresholdEvaluator:

    def __init__(self, thresholds):

        self.thresholds = thresholds

    def evaluate(self, parsed):

        alerts = []

        dashboard = parsed.get("dashboard", "")
        image = parsed.get("image")

        # ==========================================================
        # CPU
        # ==========================================================

        cpu = parsed.get("cpu")

        if (
            cpu is not None
            and self.thresholds["cpu"]["enabled"]
            and cpu >= self.thresholds["cpu"]["threshold"]
        ):

            alerts.append({
                "dashboard": dashboard,
                "metric": "CPU",
                "value": cpu,
                "threshold": self.thresholds["cpu"]["threshold"],
                "severity": "HIGH",
                "image": image
            })

            logger.warning(
                f"[ALERT] {dashboard} CPU = "
                f"{cpu}% "
                f"(Threshold: {self.thresholds['cpu']['threshold']}%)"
            )

        # ==========================================================
        # DISK
        # ==========================================================

        disk = parsed.get("disk")

        if (
            disk is not None
            and self.thresholds["disk"]["enabled"]
            and disk >= self.thresholds["disk"]["threshold"]
        ):

            alerts.append({
                "dashboard": dashboard,
                "metric": "Disk",
                "value": disk,
                "threshold": self.thresholds["disk"]["threshold"],
                "severity": "HIGH",
                "image": image
            })

            logger.warning(
                f"[ALERT] {dashboard} Disk = "
                f"{disk}% "
                f"(Threshold: {self.thresholds['disk']['threshold']}%)"
            )

        # ==========================================================
        # RDS
        # ==========================================================

        rds = parsed.get("rds")

        if (
            rds is not None
            and self.thresholds["rds"]["enabled"]
            and rds >= self.thresholds["rds"]["threshold"]
        ):

            alerts.append({
                "dashboard": dashboard,
                "metric": "RDS",
                "value": rds,
                "threshold": self.thresholds["rds"]["threshold"],
                "severity": "HIGH",
                "image": image
            })

            logger.warning(
                f"[ALERT] {dashboard} RDS = "
                f"{rds}% "
                f"(Threshold: {self.thresholds['rds']['threshold']}%)"
            )

        return alerts
