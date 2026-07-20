import yaml

with open("config/dashboards.yaml", "r") as file:
    config = yaml.safe_load(file)

for dashboard in config["dashboards"]:
    print(dashboard["name"])
    print(dashboard["url"])
    print("-" * 50)