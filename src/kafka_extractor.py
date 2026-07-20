from loguru import logger


class KafkaExtractor:

    def __init__(self, page, lag_threshold=1000):
        self.page = page
        self.lag_threshold = lag_threshold

    async def extract(self):

        empty_tables = []
        lag_tables = []

        rows = self.page.locator("tbody tr")
        total_groups = await rows.count()

        logger.info("=" * 80)
        logger.info(f"Kafka Consumer Groups Found : {total_groups}")
        logger.info("=" * 80)

        for i in range(total_groups):

            try:

                row = rows.nth(i)

                columns = await row.locator("td").all_inner_texts()

                # Expected Columns
                #
                # 0 -> Consumer Group
                # 1 -> Num Of Members
                # 2 -> Num Of Topics
                # 3 -> Consumer Lag
                # 4 -> Coordinator
                # 5 -> State

                if len(columns) < 6:
                    logger.warning(
                        f"Skipping row {i + 1} because only "
                        f"{len(columns)} columns were found."
                    )
                    continue

                table_name = columns[0].strip()
                consumer_lag = columns[3].strip()
                state = columns[5].strip().upper()

                logger.info(
                    f"{table_name} | "
                    f"Lag={consumer_lag} | "
                    f"State={state}"
                )

                # --------------------------------------------------------
                # EMPTY Consumer Group
                # --------------------------------------------------------

                if state == "EMPTY":

                    empty_tables.append(table_name)

                # --------------------------------------------------------
                # High Consumer Lag
                # --------------------------------------------------------

                if consumer_lag not in ("", "-", "N/A"):

                    try:

                        lag = int(
                            consumer_lag.replace(",", "")
                        )

                        if lag >= self.lag_threshold:

                            lag_tables.append(
                                {
                                    "table": table_name,
                                    "lag": lag
                                }
                            )

                    except ValueError:

                        logger.warning(
                            f"Unable to parse lag '{consumer_lag}' "
                            f"for {table_name}"
                        )

            except Exception:

                logger.exception(
                    f"Failed while processing row {i + 1}"
                )

        # --------------------------------------------------------
        # Overall Health
        # --------------------------------------------------------

        all_stable = (
            len(empty_tables) == 0
            and
            len(lag_tables) == 0
        )

        logger.info("=" * 80)
        logger.info(f"EMPTY Consumer Groups : {len(empty_tables)}")
        logger.info(
            f"High Consumer Lag (>={self.lag_threshold}) : "
            f"{len(lag_tables)}"
        )

        if all_stable:
            logger.success(
                "Kafka CDC Status : ALL CONSUMER GROUPS ARE STABLE"
            )
        else:
            logger.warning(
                "Kafka CDC Status : ATTENTION REQUIRED"
            )

        logger.info("=" * 80)

        return {

            "dashboard": "Kafka CDC",

            "total_groups": total_groups,

            "kafka_empty": len(empty_tables),

            "empty_tables": empty_tables,

            "lag_tables": lag_tables,

            "lag_threshold": self.lag_threshold,

            "all_stable": all_stable

        }
