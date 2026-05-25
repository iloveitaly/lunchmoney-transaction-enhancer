import socket
import backoff
import structlog

log = structlog.get_logger()

# 8 hours, in case the internet goes down overnight
MAX_WAIT_TIME = 60 * 60 * 8


@backoff.on_exception(backoff.expo, Exception, max_time=MAX_WAIT_TIME)
def wait_for_internet_connection():
    if is_internet_connected():
        return

    log.info("no internet connection, retrying...")
    # raise a generic py exception to trigger a retry
    raise Exception("no internet connection")


def is_internet_connected():
    try:
        with socket.socket(socket.AF_INET) as s:
            s.connect(("google.com", 80))
            return True
    except socket.error:
        return False
