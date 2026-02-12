import os
from .enhancer import ExtractionRule

LUNCHMONEY_API_TOKEN = os.getenv("LUNCHMONEY_API_TOKEN")
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")

# Define extraction rules here
EXTRACTION_RULES = [
    ExtractionRule(
        name="Airbnb Code",
        source_field="original_name",
        pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
        target_field="notes",
        template="Airbnb Code: {code}"
    ),
    # Add more rules here
]
