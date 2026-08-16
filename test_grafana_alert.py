import time
from datetime import datetime

from src.whatsapp import WhatsAppSender


# ============================================================
# GRAFANA ALERT MESSAGE
# ============================================================

def generate_grafana_alert():

    now = datetime.now()

    message = f"""🚨 GRAFANA ALERT

Date : {now.strftime('%d-%b-%Y')}
Time : {now.strftime('%I:%M %p')}

Total Alerts : 3

===================================

1. WINDOWS EXPORTER DASHBOARD
   Metric    : CPU Usage
   Current   : 94.2%
   Threshold : 80%

2. NODE EXPORTER FULL-KAFKA AZURE
   Metric    : CPU Usage
   Current   : 82.0%
   Threshold : 80%

3. Kafka CDC
   Metric    : Consumer Lag
   Status    : EXCEEDED
   Tables    : 1

   • connect-lead_parameters_WH
"""

    return message


# ============================================================
# SEND GRAFANA ALERT TO WHATSAPP
# ============================================================

def main():

    whatsapp = None

    try:

        # ----------------------------------------------------
        # Generate Grafana Alert
        # ----------------------------------------------------

        message = generate_grafana_alert()

        print()
        print("=" * 70)
        print("GRAFANA ALERT")
        print("=" * 70)
        print()
        print(message)
        print("=" * 70)
        print()

        # ----------------------------------------------------
        # Start WhatsApp
        # ----------------------------------------------------

        whatsapp = WhatsAppSender()

        print("Opening Grafana_Alerts...")
        print("=" * 70)

        whatsapp.start()

        # ----------------------------------------------------
        # Open Grafana Alerts WhatsApp chat
        # ----------------------------------------------------

        whatsapp.open_chat(
            whatsapp.personal_chat
        )

        # ----------------------------------------------------
        # Verify Chat
        # ----------------------------------------------------

        print()
        print("Verified chat:")
        print(whatsapp.personal_chat)
        print()

        # ----------------------------------------------------
        # Send Grafana Alert
        # ----------------------------------------------------

        print("=" * 70)
        print("Sending GRAFANA ALERT...")
        print("=" * 70)
        print()

        whatsapp.send_message(message)

        print()
        print("=" * 70)
        print("WhatsApp message sent successfully.")
        print("=" * 70)
        print()

        # ----------------------------------------------------
        # Keep Browser Open For 120 Seconds
        # ----------------------------------------------------

        print(
            "Keeping WhatsApp browser open for 120 seconds."
        )

        print(
            "Please check the Grafana_Alerts chat manually."
        )

        print()
        print("DO NOT CLOSE THE BROWSER.")
        print()

        print(
            "WhatsApp browser will remain open "
            "for 120 seconds..."
        )

        # ----------------------------------------------------
        # 120 Second Countdown
        # ----------------------------------------------------

        for remaining in range(120, 0, -10):

            print(
                f"WhatsApp browser will remain open "
                f"for {remaining} seconds..."
            )

            time.sleep(10)

        print()
        print("=" * 70)
        print("120 seconds completed.")
        print("=" * 70)
        print()

    except Exception as e:

        print()
        print("=" * 70)
        print("ERROR")
        print("=" * 70)
        print()
        print(str(e))
        print()

        raise

    finally:

        # ----------------------------------------------------
        # Close WhatsApp
        # ----------------------------------------------------

        if whatsapp:

            print()
            print("=" * 70)
            print("Closing WhatsApp...")
            print("=" * 70)
            print()

            try:

                whatsapp.close()

            except Exception as e:

                print(
                    f"WhatsApp close warning: {e}"
                )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
