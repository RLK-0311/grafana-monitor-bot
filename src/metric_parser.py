import re
from loguru import logger


class MetricParser:

    @staticmethod
    def _extract_number(text):

        # ----------------------------------------
        # Nothing to parse
        # ----------------------------------------

        if text is None:
            return None

        # ----------------------------------------
        # Already a number (from tooltip)
        # ----------------------------------------

        if isinstance(text, (int, float)):
            return float(text)

        # ----------------------------------------
        # Extract first number from text
        # ----------------------------------------

        match = re.search(r"-?\d+(?:\.\d+)?", str(text))

        if not match:
            return None

        try:
            return float(match.group())

        except Exception:
            return None

    @classmethod
    def parse(cls, dashboard_name, extracted):

        logger.info("=" * 80)
        logger.info(f"PARSING DASHBOARD : {dashboard_name}")
        logger.info("=" * 80)

        parsed = {
            "dashboard": dashboard_name,
            "cpu": None,
            "disk": None,
            "rds": None,
            "details": {}
        }

        panels = extracted.get("panels", {})

        #
        # Parse every panel
        #

        for title, content in panels.items():

            value = cls._extract_number(content)

            parsed["details"][title] = value

            logger.info(f"{title} --> {value}")

            if value is None:
                continue

            name = title.lower()

            #
            # -----------------------------
            # CPU
            # -----------------------------
            #

            if parsed["cpu"] is None:

                if (
                    "cpu busy" in name
                    or name == "cpu usage"
                    or "cpu utilization" in name
                    or "cpuutilization" in name
                    or "cpu basic" in name
                ):
                    parsed["cpu"] = value

            #
            # -----------------------------
            # DISK
            # -----------------------------
            #

            if parsed["disk"] is None:

                if (
                    "root fs used" in name
                    or "rootfs used" in name
                    or "disk usage" in name
                    or "disk space used" in name
                    or "filesystem used" in name
                    or "disk space used basic" in name
                ):
                    parsed["disk"] = value

            #
            # -----------------------------
            # RDS
            # -----------------------------
            #

            if parsed["rds"] is None:

                if (
                    "rds" in name
                    or "database connections" in name
                    or "db connection" in name
                    or "db connections" in name
                ):
                    parsed["rds"] = value

        #
        # ----------------------------------------------------------
        # Disk fallback
        # ----------------------------------------------------------
        #

        if parsed["disk"] is None:

            for title, value in parsed["details"].items():

                if value is None:
                    continue

                name = title.lower()

                if (
                    "disk" in name
                    and "total" not in name
                    and "free" not in name
                ):
                    parsed["disk"] = value
                    break

        #
        # ----------------------------------------------------------
        # CPU fallback
        # ----------------------------------------------------------
        #

        if parsed["cpu"] is None:

            for title, value in parsed["details"].items():

                if value is None:
                    continue

                name = title.lower()

                if (
                    "cpu" in name
                    and "core" not in name
                    and "cores" not in name
                    and "load" not in name
                ):
                    parsed["cpu"] = value
                    break

        logger.success(parsed)

        return parsed
