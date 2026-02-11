"""Test lunchmoney-transaction-enhancer."""

import lunchmoney_transaction_enhancer


def test_import() -> None:
    """Test that the  can be imported."""
    assert isinstance(lunchmoney_transaction_enhancer.__name__, str)