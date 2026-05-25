import os
from .enhancer import ExtractionRule

LUNCHMONEY_API_TOKEN = os.getenv("LUNCH_MONEY_API_KEY")
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")

# Define extraction rules here
EXTRACTION_RULES = [
    ExtractionRule(
        name="Airbnb Code (original_name)",
        source_field="original_name",
        pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
        target_field="notes",
        template="Airbnb Code: {code}",
    ),
    ExtractionRule(
        name="Airbnb Code (plaid_name)",
        source_field="plaid_name",
        pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
        target_field="notes",
        template="Airbnb Code: {code}",
    ),
    # Add more rules here
]
