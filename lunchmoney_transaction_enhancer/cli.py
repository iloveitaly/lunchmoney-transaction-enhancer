import click
import structlog
from whenever import Instant

from .config import EXTRACTION_RULES, HEARTBEAT_URL, LUNCHMONEY_API_TOKEN
from .enhancer import TransactionEnhancer
from .heartbeat import send_heartbeat
from .internet import wait_for_internet_connection
from .state import get_last_checked, set_last_checked

log = structlog.get_logger()


@click.command()
@click.option("--token", default=LUNCHMONEY_API_TOKEN, help="LunchMoney API Token")
@click.option("--lookback", default=7, help="Days to look back if no state found")
@click.option("--cron", is_flag=True, help="Wait for internet and send heartbeat")
def main_cmd(token, lookback, cron):
    if not token:
        log.error("lunchmoney_api_token is not set")
        return

    if cron:
        log.info("running in cron mode, waiting for internet")
        wait_for_internet_connection()

    last_checked = get_last_checked()
    if not last_checked:
        last_checked = Instant.now().add(hours=-lookback * 24)
        log.info("no last checked state, using lookback", lookback_days=lookback)

    enhancer = TransactionEnhancer(api_token=token, rules=EXTRACTION_RULES)

    # We record the current time before starting to ensure we don't miss anything
    # that happens during the run in the next cycle.
    current_run_time = Instant.now()

    try:
        enhancer.enhance_transactions(start_date=last_checked)
        set_last_checked(current_run_time)

        if cron and HEARTBEAT_URL:
            send_heartbeat(HEARTBEAT_URL)

    except Exception as e:
        log.exception("failed to enhance transactions", error=str(e))
        if cron:
            # Re-raise in cron mode to ensure the job fails visibly
            raise e


def main():
    # Configure structlog before running
    import structlog_config

    structlog_config.configure()

    main_cmd()


if __name__ == "__main__":
    main()
