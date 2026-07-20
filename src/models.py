from dataclasses import dataclass

@dataclass
class Alert:

    dashboard: str

    alert_type: str

    value: float

    threshold: float

    message: str