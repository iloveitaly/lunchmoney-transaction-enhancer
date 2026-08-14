import os

from .enhancer import ExtractionRule

LUNCHMONEY_API_TOKEN = os.getenv("LUNCH_MONEY_API_KEY")
HEARTBEAT_URL = os.getenv("HEARTBEAT_URL")


CAPITAL_ONE_TRAVEL_COMPONENTS = {
    "FLT": "Flight",
    "HTL": "Hotel",
    "CAR": "Rental Car",
    "PCH": "Premier Collection Hotel",
}


def create_capital_one_travel_rules() -> list[ExtractionRule]:
    rules = []

    for source_field in ("original_name", "plaid_name"):
        rules.append(
            ExtractionRule(
                name=f"Capital One Travel Payee ({source_field})",
                source_field=source_field,
                pattern=r"(?i)\bCOT\*(?:FLT|HTL|CAR|PCH)(?=[^A-Z]|$)",
                target_field="payee",
                template="Capital One Travel",
            )
        )

        for code, component in CAPITAL_ONE_TRAVEL_COMPONENTS.items():
            rules.append(
                ExtractionRule(
                    name=f"Capital One Travel {component} ({source_field})",
                    source_field=source_field,
                    pattern=rf"(?i)\bCOT\*{code}(?=[^A-Z]|$)",
                    target_field="notes",
                    template=f"Capital One Travel: {component}",
                )
            )

    return rules


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
    *create_capital_one_travel_rules(),
    # Add more rules here
]
