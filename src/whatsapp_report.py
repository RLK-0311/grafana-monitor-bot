from datetime import datetime


class WhatsAppReport:

    def generate(self, parsed_results, alerts):

        if not alerts:
            return None

        now = datetime.now()

        lines = []

        # ======================================================
        # Header
        # ======================================================

        lines.append("🚨 GRAFANA ALERT")
        lines.append("")
        lines.append(
            f"Date : {now.strftime('%d-%b-%Y')}"
        )
        lines.append(
            f"Time : {now.strftime('%I:%M %p')}"
        )
        lines.append("")
        lines.append(
            f"Total Alerts : {len(alerts)}"
        )
        lines.append("")
        lines.append("=" * 35)
        lines.append("")

        # ======================================================
        # Alerts
        # ======================================================

        for i, alert in enumerate(alerts, start=1):

            # ==================================================
            # Metric Alert
            # ==================================================

            if alert.get("type") == "metric":

                dashboard = alert.get(
                    "dashboard",
                    "Unknown"
                )

                metric = alert.get(
                    "metric",
                    "CPU Usage"
                )

                value = alert.get(
                    "value",
                    "N/A"
                )

                threshold = alert.get(
                    "threshold",
                    "N/A"
                )

                lines.append(
                    f"{i}. {dashboard}"
                )

                lines.append(
                    f"   Metric    : {metric}"
                )

                lines.append(
                    f"   Current   : {value}%"
                )

                lines.append(
                    f"   Threshold : {threshold}%"
                )

                lines.append("")

            # ==================================================
            # Kafka CDC Alert
            # ==================================================

            elif alert.get("type") == "kafka_empty":

                count = alert.get(
                    "count",
                    0
                )

                lines.append(
                    f"{i}. Kafka CDC"
                )

                lines.append(
                    f"   Metric    : Consumer Lag"
                )

                lines.append(
                    f"   Status    : EXCEEDED"
                )

                lines.append(
                    f"   Tables    : {count}"
                )

                lines.append("")

                for table in alert.get(
                    "tables",
                    []
                ):

                    if isinstance(table, dict):

                        lines.append(
                            f"   • {table.get('table', 'Unknown')}"
                        )

                    else:

                        lines.append(
                            f"   • {table}"
                        )

                lines.append("")

            # ==================================================
            # Unknown Alert Type
            # ==================================================

            else:

                lines.append(
                    f"{i}. {alert.get('dashboard', 'Unknown Alert')}"
                )

                lines.append("")

        return "\n".join(lines)