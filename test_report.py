from src.html_report import HTMLReport

alerts = [

    {
        "dashboard":"CM-RDS",
        "metric":"CPU",
        "value":96.4,
        "status":"CRITICAL"
    },

    {
        "dashboard":"Azure Warehouse",
        "metric":"Disk",
        "value":99.6,
        "status":"CRITICAL"
    },

    {
        "dashboard":"CM-CRON",
        "metric":"CPU",
        "value":91.2,
        "status":"WARNING"
    }

]

report = HTMLReport()

file = report.generate(alerts)

print(file)
