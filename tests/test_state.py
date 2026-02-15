import pytest
from whenever import Instant
from lunchmoney_transaction_enhancer.state import get_last_checked, set_last_checked
import lunchmoney_transaction_enhancer.state

@pytest.fixture
def mock_state_file(tmp_path, monkeypatch):
    state_dir = tmp_path / "data"
    state_file = state_dir / "last_checked.txt"
    monkeypatch.setattr(lunchmoney_transaction_enhancer.state, "STATE_DIR", state_dir)
    monkeypatch.setattr(lunchmoney_transaction_enhancer.state, "STATE_FILE", state_file)
    return state_file

def test_get_last_checked_missing(mock_state_file):
    assert get_last_checked() is None

def test_set_and_get_last_checked(mock_state_file):
    now = Instant.now()
    set_last_checked(now)
    retrieved = get_last_checked()
    assert retrieved == now

def test_get_last_checked_corrupt(mock_state_file):
    mock_state_file.parent.mkdir(parents=True, exist_ok=True)
    mock_state_file.write_text("not a date")
    assert get_last_checked() is None
