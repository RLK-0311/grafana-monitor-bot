from pathlib import Path
from datetime import datetime


class ReportGenerator:
    def __init__(self):
        Path("reports").mkdir(
            parents=True,
            exist_ok=True
        )

    def generate(
        self,
        parsed_results,
        alerts,
        success,
        failed,
    ):
        report_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        total_dashboards = len(parsed_results)
        total_alerts = len(alerts)
        healthy_dashboards = total_dashboards - total_alerts
        failed_dashboards = 0

        if not alerts:
            rows = """
    <tr>
        <td colspan="5" style="text-align:center;">
            No Alerts 🎉
        </td>
    </tr>
    """
        else:
            rows = ""
            for alert in alerts:
                alert_type = alert.get("type")

                # ==========================================================
                # Kafka Empty Table Alert
                # ==========================================================
                # This alert shape has no 'status' / 'metric' / 'value' /
                # 'threshold' keys — it carries 'tables' and 'count'
                # instead. Reading alert['status'] on this shape is what
                # caused the KeyError: 'status' crash. Render it with its
                # own layout instead of assuming the metric-alert schema.
                if alert_type == "kafka_empty":
                    metric_label = "Kafka Empty Table"
                    value_label = f"{alert.get('count', 0)} table(s)"
                    threshold_label = "-"
                    status = "ALERT"
                    status_class = "status-alert"
                    tables_str = ", ".join(alert.get("tables", []))

                    rows += f"""
<tr>
<td>{alert.get('dashboard', 'N/A')}</td>
<td>{metric_label}<br><small>{tables_str}</small></td>
<td>{value_label}</td>
<td>{threshold_label}</td>
<td class="{status_class}">
{status}
</td>
</tr>
"""

                # ==========================================================
                # Kafka High Consumer Lag Alert
                # ==========================================================
                # 'tables' here is a list of dicts: {"table": ..., "lag": ...}
                # (see kafka_extractor.py), not plain strings — pull each
                # entry apart instead of joining the dicts directly.
                elif alert_type == "kafka_lag":
                    metric_label = "Kafka Consumer Lag"
                    threshold_label = alert.get("threshold", "N/A")
                    status = "ALERT"
                    status_class = "status-alert"
                    lag_str = ", ".join(
                        f"{t.get('table', 'N/A')} ({t.get('lag', 'N/A')})"
                        for t in alert.get("tables", [])
                    )
                    value_label = f"{alert.get('count', 0)} table(s)"

                    rows += f"""
<tr>
<td>{alert.get('dashboard', 'N/A')}</td>
<td>{metric_label}<br><small>{lag_str}</small></td>
<td>{value_label}</td>
<td>{threshold_label}</td>
<td class="{status_class}">
{status}
</td>
</tr>
"""

                # ==========================================================
                # Metric Alert (CPU / RAM / Disk / RDS) — and anything
                # else that isn't explicitly 'kafka_empty' or 'kafka_lag'
                # ==========================================================
                else:
                    # .get(...) with a default instead of alert['status']
                    # so a missing key degrades to "N/A" / "ALERT" rather
                    # than crashing report generation for the whole run.
                    status = alert.get("status", "ALERT")
                    status_class = (
                        "status-alert"
                        if status == "ALERT"
                        else "status-ok"
                    )
                    rows += f"""
<tr>
<td>{alert.get('dashboard', 'N/A')}</td>
<td>{alert.get('metric', 'N/A')}</td>
<td>{alert.get('value', 'N/A')}%</td>
<td>{alert.get('threshold', 'N/A')}%</td>
<td class="{status_class}">
{status}
</td>
</tr>
"""

        html = f"""
<!DOCTYPE html>
<html>

<head>

<title>Grafana Monitoring Report</title>

<style>

body{{
    font-family:Arial,Helvetica,sans-serif;
    background:#f4f6f9;
    margin:40px;
}}

.container{{
    background:white;
    padding:30px;
    border-radius:10px;
    box-shadow:0 2px 10px rgba(0,0,0,.1);
}}

h1{{
    color:#1f4e79;
}}

table{{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}}

th{{
    background:#1f4e79;
    color:white;
    padding:10px;
}}

td{{
    border:1px solid #ddd;
    padding:8px;
}}

.alert{{
    color:red;
    font-weight:bold;
}}

.ok{{
    color:green;
    font-weight:bold;
}}

.footer{{
    margin-top:30px;
    color:#777;
    font-size:12px;
}}

.summary{{
    display:flex;
    gap:20px;
    margin-top:25px;
    margin-bottom:30px;
}}

.card{{
    flex:1;
    background:#eef4fb;
    border-radius:10px;
    padding:20px;
    text-align:center;
    border:1px solid #d0d9e5;
}}

.card h2{{
    margin:0;
    color:#1f4e79;
    font-size:28px;
}}

.card p{{
    margin-top:10px;
    font-weight:bold;
    color:#444;
}}

.status-ok{{
    color:#2e7d32;
    font-weight:bold;
}}

.status-alert{{
    color:#d32f2f;
    font-weight:bold;
}}

</style>

</head>

<body>

<div class="container">

<h1>Grafana Monitoring Report</h1>

<p><b>Generated:</b> {report_time}</p>

<hr>

<div class="summary">

<div class="card">
<h2>{total_dashboards}</h2>
<p>Total Dashboards</p>
</div>

<div class="card">
<h2>{healthy_dashboards}</h2>
<p>Healthy</p>
</div>

<div class="card">
<h2>{total_alerts}</h2>
<p>Alerts</p>
</div>

<div class="card">
<h2>{failed_dashboards}</h2>
<p>Failed</p>
</div>

</div>

<h2>Summary</h2>
<p><b>Successful Dashboards:</b> {success}</p>
<p><b>Failed Dashboards:</b> {failed}</p>
<p><b>Total Alerts:</b> {len(alerts)}</p>

<h2>Alert Details</h2>
<table>
<tr>
<th>Dashboard</th>
<th>Metric</th>
<th>Value</th>
<th>Threshold</th>
<th>Status</th>
</tr>
{rows}
</table>

<div class="footer">

Generated automatically by Grafana Monitoring Bot

</div>

</div>

</body>

</html>
"""
        with open(
            "reports/report.html",
            "w",
            encoding="utf-8"
        ) as file:
            file.write(html)
        print("=" * 60)
        print("HTML Report Generated")
        print("reports/report.html")
        print("=" * 60)