import asyncio
from pathlib import Path
from loguru import logger

# Create logs directory
Path("logs").mkdir(exist_ok=True)

# Clear bot.log every run
Path("logs/bot.log").write_text("")

from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")

for log_file in Path("logs").glob("grafana_monitor_*.log"):
    if today not in log_file.name:
        log_file.unlink()

from src.config_loader import ConfigLoader
from src.browser_manager import BrowserManager
from src.dashboard_capture import DashboardCapture
from src.metric_extractor import MetricExtractor
from src.metric_parser import MetricParser
from src.alert_evaluator import AlertEvaluator
from src.report_generator import ReportGenerator
from src.whatsapp_report import WhatsAppReport
from src.whatsapp import WhatsAppSender


# ==============================================================================
# LOGGING
# ==============================================================================
logger.add(
    "logs/grafana_monitor_{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="00:00",  # Create a new log file every day at midnight
    retention="1 day", # Automatically delete logs older than 1 day
    enqueue=True,
)


# ==============================================================================
# WHATSAPP UPLOAD HELPER
# ==============================================================================
#
# WhatsAppSender uses Playwright's SYNC API, but main() runs inside an
# asyncio event loop (this whole bot.py is async, for the Grafana browser
# automation). Playwright's sync API refuses to run inside an active event
# loop, so this whole sequence runs in a separate thread via
# asyncio.to_thread(). Everything here (start/open_chat/send_image/close)
# must run in the SAME thread, since they share the same Playwright
# page/context objects — that's why it's all one function instead of
# separate to_thread() calls per step.
def _send_screenshots_via_whatsapp(whatsapp, summary_message, screenshot_paths):
    whatsapp.start()
    try:
        # Personal chat — alert summary only, no screenshots
        whatsapp.open_chat(whatsapp.personal_chat)

        print("=" * 80)
        print("summary_message =", repr(summary_message))
        print("=" * 80)

        if summary_message:
            logger.info("Sending WhatsApp summary...")
            whatsapp.send_message(summary_message)

        # Monitoring group — all screenshots, no alert message
        whatsapp.open_chat(whatsapp.group_chat)

        if screenshot_paths:

            logger.info(
                f"Uploading {len(screenshot_paths)} screenshot(s) "
                f"to {whatsapp.group_chat} as a single album..."
            )
            for screenshot in screenshot_paths:
                logger.info(f"Uploading : {screenshot}")
            whatsapp.send_images(screenshot_paths)
        else:

            logger.info("No screenshots to upload.")
    finally:
        # Restored: without this the WhatsApp Playwright context/profile
        # is never released, which produces the same "already in use by
        # another instance" failure on the next run that the Grafana
        # browser profile was hitting.
        whatsapp.close()


# ==============================================================================
# MAIN
# ==============================================================================
async def main():
    logger.info("=" * 80)
    logger.info("🚀 Starting Grafana Monitoring Bot")
    logger.info("=" * 80)

    # Declared before the try block so the finally clause can always
    # check whether a browser was actually created, even if something
    # fails during config loading or before browser.start() completes.
    browser = None

    try:
        # ======================================================================
        # LOAD CONFIGURATION
        # ======================================================================
        logger.info("Loading configuration files...")
        loader = ConfigLoader()
        config = loader.load_all()
        logger.success("Configuration loaded successfully.")
        # ======================================================================
        # DISPLAY CONFIGURATION
        # ======================================================================
        logger.info("Loaded Settings")
        logger.info(config["settings"])
        logger.info("Loaded Thresholds")
        logger.info(config["thresholds"])
        logger.info(
            f"Total Dashboards : {len(config['dashboards']['dashboards'])}"
        )
        # ======================================================================
        # START BROWSER
        # ======================================================================
        logger.info("Launching Chrome...")
        browser = BrowserManager(config["settings"])
        page = await browser.start()
        logger.success("Chrome Browser Started.")
        # ======================================================================
        # INITIALIZE COMPONENTS
        # ======================================================================
        capture = DashboardCapture(
            page,
            config["settings"]
        )
        extractor = MetricExtractor(page)
        parser = MetricParser()
        evaluator = AlertEvaluator(
            config["thresholds"]
        )
        report = ReportGenerator()
        whatsapp_report = WhatsAppReport()
        whatsapp = WhatsAppSender()
        dashboards = config["dashboards"]["dashboards"]
        success = 0
        failed = 0
        parsed_results = []
        alerts = []
        screenshot_paths = []
        alert_images = []
        logger.info("=" * 80)
        logger.info("Starting Dashboard Processing")
        logger.info("=" * 80)
        # ======================================================================
        # PROCESS DASHBOARDS
        # ======================================================================
        for index, dashboard in enumerate(dashboards, start=1):
            logger.info("=" * 80)
            logger.info(
                f"[{index}/{len(dashboards)}] Processing : {dashboard['name']}"
            )
            logger.info("=" * 80)
            image_path = await capture.capture_dashboard(dashboard)
            if image_path:
                logger.info(f"Captured : {image_path}")
            if image_path is None:
                failed += 1
                continue
            success += 1
            screenshot_paths.append(image_path)
            # ==============================================================
            # Extract Metrics
            # ==============================================================
            if dashboard["name"] == "KAFKA_CDC":

                from src.kafka_extractor import KafkaExtractor

                lag_threshold = config["thresholds"]["kafka"]["lag_threshold"]

                kafka = KafkaExtractor(
                    page,
                    lag_threshold=lag_threshold
                )

                parsed = await kafka.extract()

            else:

                metrics = await extractor.extract_metrics()

                parsed = parser.parse(
                    dashboard["name"],
                    metrics
                )

            parsed["image"] = image_path
            print("=" * 60)
            print("PARSED RESULT")
            print(parsed)
            print("=" * 60)
            parsed_results.append(parsed)
            logger.success("Parsed Metrics")
            logger.success(parsed)

            print("=" * 80)
            print("CURRENT DASHBOARD =", parsed["dashboard"])
            print("PARSED =", parsed)
            print("=" * 80)

            # ==============================================================
            # Evaluate Thresholds
            # ==============================================================
            # Moved inside the loop: this must run once per dashboard,
            # right after that dashboard's own `parsed` is built. Running
            # it after the loop would only ever evaluate the LAST
            # dashboard processed (or crash with NameError if the last
            # dashboard's capture failed and `continue` was hit before
            # `parsed` was created).
            dashboard_alerts = evaluator.evaluate(parsed)
            print("=" * 80)
            print("Dashboard :", parsed["dashboard"])
            print("CPU       :", parsed.get("cpu"))
            print("DISK      :", parsed.get("disk"))
            print("RDS       :", parsed.get("rds"))
            print("Generated :", dashboard_alerts)
            print("=" * 80)

            alerts.extend(dashboard_alerts)
            for alert in dashboard_alerts:
                if alert["image"] not in alert_images:
                    alert_images.append(alert["image"])
        # ======================================================================
        # DISPLAY ALL PARSED METRICS
        # ======================================================================
        logger.info("=" * 80)
        logger.info("Parsed Dashboard Metrics")
        logger.info("=" * 80)
        for metric in parsed_results:
            logger.info(metric)

        # ======================================================================
        # DISPLAY GENERATED ALERTS
        # ======================================================================

        logger.info("=" * 80)
        logger.info("Generated Alerts")
        logger.info("=" * 80)

        if alerts:

            logger.warning(f"Total Alerts Generated : {len(alerts)}")

            for index, alert in enumerate(alerts, start=1):

                logger.warning("-" * 60)
                logger.warning(f"Alert #{index}")
                logger.warning(f"Dashboard : {alert.get('dashboard', 'N/A')}")

                # ==========================================================
                # Metric Alert (CPU / RAM / Disk / RDS)
                # ==========================================================
                if alert.get("type") == "metric":

                    logger.warning(f"Metric    : {alert.get('metric', 'N/A')}")
                    logger.warning(f"Value     : {alert.get('value', 'N/A')}%")
                    logger.warning(f"Threshold : {alert.get('threshold', 'N/A')}%")
                    logger.warning(f"Severity  : {alert.get('severity', 'N/A')}")
                    logger.warning(f"Image     : {alert.get('image', 'N/A')}")

                # ==========================================================
                # Kafka Empty Table Alert
                # ==========================================================
                elif alert.get("type") == "kafka_empty":

                    logger.warning("Type      : Kafka Empty Table")
                    logger.warning(f"Tables    : {', '.join(alert.get('tables', []))}")
                    logger.warning(f"Count     : {alert.get('count', 0)}")
                    logger.warning(f"Image     : {alert.get('image', 'N/A')}")

                # ==========================================================
                # Kafka High Consumer Lag Alert
                # ==========================================================
                # 'tables' is a list of dicts here ({"table": ..., "lag": ...}),
                # not plain strings — join() on it directly would raise
                # TypeError, so format each entry explicitly.
                elif alert.get("type") == "kafka_lag":

                    lag_str = ", ".join(
                        f"{t.get('table', 'N/A')} ({t.get('lag', 'N/A')})"
                        for t in alert.get("tables", [])
                    )
                    logger.warning("Type      : Kafka High Consumer Lag")
                    logger.warning(f"Tables    : {lag_str}")
                    logger.warning(f"Count     : {alert.get('count', 0)}")
                    logger.warning(f"Threshold : {alert.get('threshold', 'N/A')}")
                    logger.warning(f"Image     : {alert.get('image', 'N/A')}")

                # ==========================================================
                # Unknown Alert Type
                # ==========================================================
                else:

                    logger.warning(f"Alert Data : {alert}")

        else:

            logger.success("No alerts generated.")

        # ==============================================================
        # Generate HTML Report
        # ==============================================================
        report.generate(
            parsed_results,
            alerts,
            success,
            failed
        )
        logger.info("=" * 80)
        logger.info("Captured Screenshot Files")
        logger.info("=" * 80)
        for file in screenshot_paths:
            logger.info(file)
        # ======================================================================
        # SEND SCREENSHOTS TO WHATSAPP
        # ======================================================================
        # ==============================================================
        # Generate WhatsApp Summary
        # ==============================================================

        print("=" * 80)
        print("FINAL ALERTS")
        print(alerts)
        print("COUNT =", len(alerts))
        print("=" * 80)

        summary_message = whatsapp_report.generate(
            parsed_results,
            alerts
        )

        print("=" * 80)
        print("SUMMARY MESSAGE")
        print("=" * 80)
        print(summary_message)
        print("=" * 80)
        print(f"Alerts Count = {len(alerts)}")
        print("=" * 80)

        logger.info("=" * 80)
        logger.info("Uploading Screenshots to WhatsApp")
        logger.info("=" * 80)

        await asyncio.to_thread(
            _send_screenshots_via_whatsapp,
            whatsapp,
            summary_message,
            screenshot_paths
        )

        logger.success("All screenshots uploaded successfully.")
        # ======================================================================
        # SUMMARY
        # ======================================================================
        logger.info("=" * 80)
        logger.info("Dashboard Capture Summary")
        logger.info("=" * 80)
        logger.success(f"Successful Dashboards : {success}")
        logger.error(f"Failed Dashboards     : {failed}")
        logger.success(f"Total Dashboards      : {success + failed}")
        # ======================================================================
        # UPCOMING PHASES
        # ======================================================================
        logger.info("=" * 80)
        logger.info("Upcoming Phases")
        logger.info("=" * 80)
        logger.info("Send Office Email")
        logger.info("Delete Screenshots After 5 Minutes")

        # These only run if everything above succeeded — moved out of the
        # old bare tail-of-function position (which was after the
        # try/except/finally and therefore ran unconditionally, even on
        # exception) and back inside the try, right after the last real
        # step. A failed run now correctly ends on the exception log
        # instead of also claiming success underneath it.
        logger.success("=" * 80)
        logger.success("Grafana Monitoring Bot Finished Successfully")
        logger.success("=" * 80)

    except Exception as e:
        logger.exception(f"Application Error : {e}")

    finally:
        # ======================================================================
        # CLOSE BROWSER
        # ======================================================================
        # Runs no matter how the try block exits (success, exception, or
        # an early failure inside browser.start() itself) so the Chromium
        # profile lock at browser/profile is always released. Without
        # this, any run that raises before reaching the old end-of-try
        # browser.stop() call left a Chrome process holding the profile,
        # and the *next* run failed immediately with:
        #   "Opening in existing browser session... profile is already
        #   in use by another instance of Chromium."
        if browser is not None:
            try:
                logger.info("Closing Chrome Browser...")
                await browser.stop()
                logger.success("Browser Closed Successfully.")
            except Exception as close_err:
                # Don't let a failure while closing mask the original
                # error, or crash the finally block itself.
                logger.warning(f"Error while closing browser : {close_err}")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    asyncio.run(main())