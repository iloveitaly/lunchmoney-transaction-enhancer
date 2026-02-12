from whenever import Instant
from pathlib import Path

STATE_FILE = Path("last_checked.txt")

def get_last_checked() -> Instant | None:
    if not STATE_FILE.exists():
        return None
    
    try:
        timestamp = STATE_FILE.read_text().strip()
        return Instant.from_iso8601(timestamp)
    except Exception:
        return None

def set_last_checked(instant: Instant):
    STATE_FILE.write_text(instant.format_iso8601())
