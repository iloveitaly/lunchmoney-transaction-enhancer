import socket

import structlog
from tenacity import retry, retry_if_exception_type, stop_after_delay, wait_exponential

log = structlog.get_logger()

# 8 hours, in case the internet goes down overnight
MAX_WAIT_TIME = 60 * 60 * 8


class NoInternetConnectionError(Exception):
    """Raised when a connectivity check fails and a retry should be attempted."""


@retry(
    retry=retry_if_exception_type(NoInternetConnectionError),
    stop=stop_after_delay(MAX_WAIT_TIME),
    wait=wait_exponential(multiplier=1, min=2, max=60),
    reraise=True,
)
def wait_for_internet_connection():
    if is_internet_connected():
        return

    log.info("no internet connection, retrying...")
    raise NoInternetConnectionError("no internet connection")


def is_internet_connected():
    try:
        with socket.socket(socket.AF_INET) as s:
            s.connect(("google.com", 80))
            return True
    except OSError:
        return False
