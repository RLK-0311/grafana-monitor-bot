import yaml
from pathlib import Path


class ConfigLoader:

    def __init__(self):
        self.config_dir = Path("config")

    def load_yaml(self, filename):
        file_path = self.config_dir / filename

        with open(file_path, "r") as f:
            return yaml.safe_load(f)

    def load_all(self):

        return {
            "dashboards": self.load_yaml("dashboards.yaml"),
            "thresholds": self.load_yaml("thresholds.yaml"),
            "settings": self.load_yaml("settings.yaml")
        }