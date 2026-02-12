import requests
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

log = structlog.get_logger()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=False
)
def send_heartbeat(url: str) -> None:
    """
    Send a GET request to a heartbeat URL with exponential backoff.
    """
    if not url:
        return

    log.info("sending heartbeat", url=url)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        log.error("heartbeat failed", url=url, error=str(e))
        raise e
