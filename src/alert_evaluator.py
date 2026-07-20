from datetime import datetime
from loguru import logger


class AlertEvaluator:

    def __init__(self, thresholds):
        self.thresholds = thresholds

    def evaluate(self, parsed):

        alerts = []

        dashboard = parsed.get("dashboard", "")
        image = parsed.get("image")

        # ==========================================================
        # CPU / DISK / RDS
        # ==========================================================

        metric_mapping = {
            "cpu": "CPU",
            "disk": "DISK",
            "rds": "RDS",
        }

        for key, display_name in metric_mapping.items():

            value = parsed.get(key)

            if value is None:
                continue

            if isinstance(value, list):
                values = value
            else:
                values = [value]

            config = self.thresholds.get(key)

            if not config:
                continue

            if not config.get("enabled", False):
                continue

            threshold = config["threshold"]

            for current_value in values:

                if current_value >= threshold:

                    difference = current_value - threshold

                    if difference >= 5:
                        severity = "CRITICAL"
                    elif difference >= 2:
                        severity = "HIGH"
                    else:
                        severity = "WARNING"

                    alerts.append(
                        {
                            "type": "metric",
                            "status": "ALERT",
                            "dashboard": dashboard,
                            "metric": display_name,
                            "value": current_value,
                            "threshold": threshold,
                            "severity": severity,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "image": image,
                        }
                    )

                    logger.warning(
                        f"{dashboard} | "
                        f"{display_name}={current_value}% "
                        f"(Threshold {threshold}%)"
                    )

        # ==========================================================
        # Kafka EMPTY Consumer Groups
        # ==========================================================

        logger.info(f"Dashboard Name Received = {dashboard}")

        if "KAFKA" in dashboard.upper():

            empty_tables = parsed.get("empty_tables", [])

            if empty_tables:

                alerts.append(
                    {
                        "type": "kafka_empty",
                        "dashboard": dashboard,
                        "tables": empty_tables,
                        "count": len(empty_tables),
                        "image": image,
                    }
                )

                logger.warning(
                    f"Kafka EMPTY Consumer Groups : {len(empty_tables)}"
                )

        # ==========================================================
        # Kafka High Consumer Lag
        # ==========================================================

            lag_tables = parsed.get("lag_tables", [])

            if lag_tables:

                alerts.append(
                    {
                        "type": "kafka_lag",
                        "dashboard": dashboard,
                        "tables": lag_tables,
                        "count": len(lag_tables),
                        "threshold": parsed.get("lag_threshold", 1000),
                        "image": image,
                    }
                )

                logger.warning(
                    f"Kafka High Consumer Lag : {len(lag_tables)}"
                )

        return alerts
