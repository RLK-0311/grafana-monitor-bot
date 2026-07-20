from pathlib import Path
from datetime import datetime
from jinja2 import Template


class HTMLReport:

    def __init__(self):
        Path("reports").mkdir(exist_ok=True)

    def generate(self, alerts):

        html = """
<!DOCTYPE html>
<html>

<head>

<meta charset="UTF-8">

<title>Grafana Monitoring Report</title>

<style>

body{
background:#0f172a;
font-family:Arial;
color:white;
padding:30px;
}

h1{
color:#4fc3f7;
}

table{

width:100%;
border-collapse:collapse;
margin-top:25px;

}

th{

background:#1e293b;
padding:12px;

}

td{

padding:12px;
background:#162033;
border-bottom:1px solid #263248;

}

.ok{

color:#5ee27d;
font-weight:bold;

}

.warning{

color:#ffd54f;
font-weight:bold;

}

.critical{

color:#ff5252;
font-weight:bold;

}

.footer{

margin-top:40px;
font-size:13px;
color:#8fa3c0;

}

</style>

</head>

<body>

<h1>Grafana Monitoring Report</h1>

<p>

Generated :
{{ time }}

</p>

<table>

<tr>

<th>Dashboard</th>

<th>Metric</th>

<th>Value</th>

<th>Status</th>

</tr>

{% for a in alerts %}

<tr>

<td>{{a.dashboard}}</td>

<td>{{a.metric}}</td>

<td>{{a.value}}%</td>

<td class="{{a.status.lower()}}">

{{a.status}}

</td>

</tr>

{% endfor %}

</table>

<div class="footer">

Grafana Monitoring Bot

</div>

</body>

</html>

"""

        template = Template(html)

        output = template.render(

            alerts=alerts,

            time=datetime.now().strftime("%d-%m-%Y %H:%M:%S")

        )

        file = "reports/report.html"

        with open(file, "w", encoding="utf-8") as f:
            f.write(output)

        return file