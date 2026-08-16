from src.whatsapp_report import WhatsAppReport
from src.whatsapp import WhatsAppSender


def main():

    # ==========================================================
    # TEST ALERT DATA
    # ==========================================================

    alerts = [
        {
            "type": "metric",
            "dashboard": "WINDOWS EXPORTER DASHBOARD",
            "metric": "CPU Usage",
            "value": 94.2,
            "threshold": 80,
        },
        {
            "type": "metric",
            "dashboard": "NODE EXPORTER FULL-KAFKA AZURE",
            "metric": "CPU Usage",
            "value": 82.0,
            "threshold": 80,
        },
        {
            "type": "kafka_empty",
            "dashboard": "KAFKA_CDC",
            "tables": [
                "connect-lead_parameters_WH"
            ],
            "count": 1,
        },
    ]

    # ==========================================================
    # GENERATE GRAFANA ALERT
    # ==========================================================

    report = WhatsAppReport()

    message = report.generate(
        parsed_results=[],
        alerts=alerts
    )

    print()
    print("=" * 70)
    print("GRAFANA ALERT TO BE SENT")
    print("=" * 70)
    print(message)
    print("=" * 70)

    # ==========================================================
    # START WHATSAPP
    # ==========================================================

    whatsapp = WhatsAppSender()

    try:

        print()
        print("Opening WhatsApp...")

        whatsapp.start()

        # ======================================================
        # IMPORTANT:
        # Send ONLY to personal_chat
        # Do NOT open group_chat
        # Do NOT send screenshots
        # ======================================================

        print(
            f"Opening chat: {whatsapp.personal_chat}"
        )

        whatsapp.open_chat(
            whatsapp.personal_chat
        )

        # ======================================================
        # SEND ONLY GRAFANA ALERT
        # ======================================================

        print()
        print("Sending GRAFANA ALERT...")
        print()

        whatsapp.send_message(message)

        print()
        print("=" * 70)
        print("GRAFANA ALERT SENT SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:

        print()
        print("=" * 70)
        print("WHATSAPP ALERT TEST FAILED")
        print("=" * 70)
        print(e)
        print("=" * 70)

        raise

    finally:

        print()
        print("Closing WhatsApp...")

        whatsapp.close()

        print("WhatsApp closed.")


if __name__ == "__main__":
    main()
