from unittest.mock import patch

import pytest
from lunchable.models import TransactionObject
from structlog.testing import capture_logs
from whenever import Instant

from lunchmoney_transaction_enhancer.config import EXTRACTION_RULES
from lunchmoney_transaction_enhancer.enhancer import ExtractionRule, TransactionEnhancer


@pytest.fixture
def mock_transaction():
    return TransactionObject(
        id=123,
        date="2024-01-01",
        payee="Airbnb",
        amount=100.0,
        currency="usd",
        original_name="AIRBNB * HMFSTBA35Y",
        notes=None,
        status="cleared",
        is_pending=False,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )


def test_transaction_enhancer_updates(mock_transaction):
    rule = ExtractionRule(
        name="Airbnb Code",
        source_field="original_name",
        pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
        target_field="notes",
        template="Code: {code}",
    )

    with patch("lunchmoney_transaction_enhancer.enhancer.LunchMoney") as mock_lm_class:
        mock_lm = mock_lm_class.return_value
        mock_lm.get_transactions.return_value = [mock_transaction]

        enhancer = TransactionEnhancer(api_token="fake", rules=[rule])
        count = enhancer.enhance_transactions(start_date=Instant.from_utc(2024, 1, 1))

        assert count == 1
        mock_lm.get_transactions.assert_called_once()
        mock_lm.update_transaction.assert_called_once()

        # Verify update object
        args, _kwargs = mock_lm.update_transaction.call_args
        assert args[0] == 123
        assert args[1].notes == "Code: HMFSTBA35Y"


def test_transaction_enhancer_uses_next_day_for_same_day_run():
    start_date = Instant.from_utc(2024, 1, 1, 10)
    current_time = Instant.from_utc(2024, 1, 1, 12)

    with (
        patch("lunchmoney_transaction_enhancer.enhancer.LunchMoney") as mock_lm_class,
        patch("lunchmoney_transaction_enhancer.enhancer.Instant") as mock_instant,
    ):
        mock_lm = mock_lm_class.return_value
        mock_lm.get_transactions.return_value = []
        mock_instant.now.return_value = current_time

        enhancer = TransactionEnhancer(api_token="fake", rules=[])
        count = enhancer.enhance_transactions(start_date=start_date)

        assert count == 0
        mock_lm.get_transactions.assert_called_once_with(
            start_date="2024-01-01",
            end_date="2024-01-02",
        )


def test_transaction_enhancer_no_change_needed(mock_transaction):
    # If the target field already matches the template, don't update
    mock_transaction.notes = "Code: HMFSTBA35Y"
    rule = ExtractionRule(
        name="Airbnb Code",
        source_field="original_name",
        pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
        target_field="notes",
        template="Code: {code}",
    )

    with patch("lunchmoney_transaction_enhancer.enhancer.LunchMoney") as mock_lm_class:
        mock_lm = mock_lm_class.return_value
        mock_lm.get_transactions.return_value = [mock_transaction]

        enhancer = TransactionEnhancer(api_token="fake", rules=[rule])
        count = enhancer.enhance_transactions(start_date=Instant.from_utc(2024, 1, 1))

        assert count == 0
        mock_lm.update_transaction.assert_not_called()


def test_transaction_enhancer_preserves_existing_notes(mock_transaction):
    mock_transaction.notes = "Old notes"
    rule = ExtractionRule(
        name="Airbnb Code",
        source_field="original_name",
        pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
        target_field="notes",
        template="Code: {code}",
    )

    with patch("lunchmoney_transaction_enhancer.enhancer.LunchMoney") as mock_lm_class:
        mock_lm = mock_lm_class.return_value
        mock_lm.get_transactions.return_value = [mock_transaction]

        enhancer = TransactionEnhancer(api_token="fake", rules=[rule])
        with capture_logs() as cap_logs:
            count = enhancer.enhance_transactions(
                start_date=Instant.from_utc(2024, 1, 1)
            )

        assert count == 0
        mock_lm.update_transaction.assert_not_called()
        assert any(
            log.get("event") == "skipping note update because notes are already set"
            and log.get("log_level") == "warning"
            for log in cap_logs
        )


def test_transaction_enhancer_preserves_notes_and_applies_other_updates(
    mock_transaction,
):
    mock_transaction.notes = "Old notes"
    rules = [
        ExtractionRule(
            name="Airbnb Code",
            source_field="original_name",
            pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
            target_field="notes",
            template="Code: {code}",
        ),
        ExtractionRule(
            name="Airbnb Payee",
            source_field="original_name",
            pattern=r"AIRBNB",
            target_field="payee",
            template="Airbnb stay",
        ),
    ]

    with patch("lunchmoney_transaction_enhancer.enhancer.LunchMoney") as mock_lm_class:
        mock_lm = mock_lm_class.return_value
        mock_lm.get_transactions.return_value = [mock_transaction]

        enhancer = TransactionEnhancer(api_token="fake", rules=rules)
        count = enhancer.enhance_transactions(start_date=Instant.from_utc(2024, 1, 1))

        assert count == 1
        mock_lm.update_transaction.assert_called_once()
        args, _kwargs = mock_lm.update_transaction.call_args
        assert args[0] == 123
        assert args[1].payee == "Airbnb stay"
        assert args[1].notes is None


@pytest.mark.parametrize("source_field", ["original_name", "plaid_name"])
@pytest.mark.parametrize(
    ("descriptor", "expected_notes"),
    [
        ("COT*FLT", "Flight"),
        ("COT*HTL *ABC123*", "Hotel"),
        ("COT*CAR *ABC123*", "Rental Car"),
        ("COT*PCH627-23633070MA", "Premier Collection Hotel"),
    ],
)
def test_capital_one_travel_rules(
    mock_transaction,
    source_field,
    descriptor,
    expected_notes,
):
    mock_transaction.original_name = None
    if source_field == "original_name":
        mock_transaction.original_name = descriptor
    else:
        mock_transaction.plaid_metadata = {"name": descriptor}

    updates = {}
    for rule in EXTRACTION_RULES:
        result = rule.apply(mock_transaction)
        if result:
            updates.update(result)

    assert updates == {
        "payee": "Capital One Travel",
        "notes": expected_notes,
    }


@pytest.mark.parametrize("source_field", ["original_name", "plaid_name"])
@pytest.mark.parametrize(
    ("descriptor", "expected_notes"),
    [
        (
            "DEPOSIT DIVIDEND ANNUAL PERCENTAGE YIELD EARNED 4.30% "
            "FOR PERIOD FROM 02/01/26 THRU 02/28/26",
            "Interest: 4.30% APY (02/01/26 to 02/28/26)",
        ),
        (
            "WITHDRAWAL ACH WISE US INC TYPE: WISE ID: 9453233521 "
            "DATA: 91309152 CO: WISE US INC",
            "Wise transfer: 91309152",
        ),
    ],
)
def test_additional_note_rules(
    mock_transaction,
    source_field,
    descriptor,
    expected_notes,
):
    mock_transaction.original_name = None
    if source_field == "original_name":
        mock_transaction.original_name = descriptor
    else:
        mock_transaction.plaid_metadata = {"name": descriptor}

    updates = {}
    for rule in EXTRACTION_RULES:
        result = rule.apply(mock_transaction)
        if result:
            updates.update(result)

    assert updates == {"notes": expected_notes}


def test_extraction_rule_named_groups(mock_transaction):
    rule = ExtractionRule(
        name="Airbnb Code",
        source_field="original_name",
        pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
        target_field="notes",
        template="Code: {code}",
    )
    result = rule.apply(mock_transaction)
    assert result == {"notes": "Code: HMFSTBA35Y"}


def test_extraction_rule_positional_groups(mock_transaction):
    rule = ExtractionRule(
        name="Airbnb Code",
        source_field="original_name",
        pattern=r"AIRBNB \* ([A-Z0-9]{10})",
        target_field="notes",
        template="Code: {g1}",
    )
    result = rule.apply(mock_transaction)
    assert result == {"notes": "Code: HMFSTBA35Y"}


def test_extraction_rule_no_groups(mock_transaction):
    rule = ExtractionRule(
        name="Airbnb Match",
        source_field="payee",
        pattern=r"Airbnb",
        target_field="notes",
        template="Matched: {match}",
    )
    result = rule.apply(mock_transaction)
    assert result == {"notes": "Matched: Airbnb"}


def test_extraction_rule_no_match(mock_transaction):
    rule = ExtractionRule(
        name="No Match",
        source_field="payee",
        pattern=r"Uber",
        target_field="notes",
        template="{match}",
    )
    result = rule.apply(mock_transaction)
    assert result is None


def test_extraction_rule_missing_source_field(mock_transaction):
    rule = ExtractionRule(
        name="Invalid Field",
        source_field="non_existent_field",
        pattern=r".*",
        target_field="notes",
        template="{match}",
    )
    result = rule.apply(mock_transaction)
    assert result is None


def test_extraction_rule_template_error(mock_transaction):
    rule = ExtractionRule(
        name="Bad Template",
        source_field="payee",
        pattern=r"(?P<name>.*)",
        target_field="notes",
        template="{wrong_key}",
    )
    with capture_logs() as cap_logs:
        result = rule.apply(mock_transaction)

    assert result is None
    assert any("template error" in log.get("event", "") for log in cap_logs)
