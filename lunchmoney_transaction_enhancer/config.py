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


def create_note_rules(
    name: str,
    pattern: str,
    template: str,
) -> list[ExtractionRule]:
    return [
        ExtractionRule(
            name=f"{name} ({source_field})",
            source_field=source_field,
            pattern=pattern,
            target_field="notes",
            template=template,
        )
        for source_field in ("original_name", "plaid_name")
    ]


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
                    template=component,
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
    *create_note_rules(
        name="Alliant Interest",
        pattern=(
            r"(?i)ANNUAL PERCENTAGE YIELD EARNED\s+"
            r"(?P<apy>\d+\.\d+)%\s+FOR PERIOD FROM\s+"
            r"(?P<start>\d{2}/\d{2}/\d{2,4})\s+THRU\s+"
            r"(?P<end>\d{2}/\d{2}/\d{2,4})"
        ),
        template="Interest: {apy}% APY ({start} to {end})",
    ),
    *create_note_rules(
        name="Wise Transfer Reference",
        pattern=(
            r"(?i)\bWITHDRAWAL ACH WISE(?: US)? INC\s+"
            r"TYPE:\s*WISE\b.*?\bDATA:\s*(?P<reference>\d{8})\b"
        ),
        template="Wise transfer: {reference}",
    ),
    # Add more rules here
]
