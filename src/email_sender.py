import os
from email.message import EmailMessage

import aiosmtplib
from loguru import logger


class EmailSender:

    def __init__(
        self,
        smtp_server,
        smtp_port,
        username,
        password,
        sender,
        receiver,
    ):

        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender = sender
        self.receiver = receiver

    async def send_html(self, report_path):

        try:

            msg = EmailMessage()

            msg["Subject"] = "Grafana Monitoring Report"

            msg["From"] = self.sender

            msg["To"] = self.receiver

            with open(report_path, "r", encoding="utf-8") as f:
                html = f.read()

            msg.set_content("Grafana Monitoring Report")

            msg.add_alternative(html, subtype="html")

            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.username,
                password=self.password,
            )

            logger.success("Email Sent Successfully.")

        except Exception as e:

            logger.exception(e)