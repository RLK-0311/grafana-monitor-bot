from datetime import datetime


class WhatsAppReport:

    def generate(self, parsed_results, alerts):

        if not alerts:
            return None

        now = datetime.now()

        lines = []

        lines.append("🚨 GRAFANA ALERT")
        lines.append("")
        lines.append(f"Date : {now.strftime('%d-%b-%Y')}")
        lines.append(f"Time : {now.strftime('%I:%M %p')}")
        lines.append("")
        lines.append(f"Total Alerts : {len(alerts)}")
        lines.append("")
        lines.append("=" * 35)
        lines.append("")

        for i, alert in enumerate(alerts, start=1):

            # ======================================================
            # Metric Alerts
            # ======================================================
            if alert.get("type") == "metric":

                lines.append(
                    f"{i}. {alert.get('dashboard', 'Unknown')} --> "
                    f"{alert.get('value', 'N/A')}% "
                    f"(Threshold {alert.get('threshold', 'N/A')}%)"
                )

            # ======================================================
            # Kafka Empty Table Alerts
            # ======================================================
            elif alert.get("type") == "kafka_empty":

                lines.append(
                    f"{i}. Kafka CDC "
                    f"({alert.get('count', 0)} table(s) exceeded lag)"
                )

                for table in alert.get("tables", []):

                    if isinstance(table, dict):

                        lines.append(
                            f"     • {table.get('table', 'Unknown')} "
                            f"(Lag: {table.get('lag', 'N/A')})"
                        )

                    else:

                        lines.append(f"     • {table}")

            # ======================================================
            # Unknown Alert Type
            # ======================================================
            else:

                lines.append(
                    f"{i}. {alert.get('dashboard', 'Unknown Alert')}"
                )

        return "\n".join(lines)