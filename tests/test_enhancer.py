from unittest.mock import patch

import pytest
from lunchable.models import TransactionObject
from structlog.testing import capture_logs
from whenever import Instant

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
        notes="Old notes",
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
