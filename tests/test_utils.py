from unittest.mock import patch

import pytest
import requests
from structlog.testing import capture_logs
from tenacity import RetryError

from lunchmoney_transaction_enhancer.heartbeat import send_heartbeat
from lunchmoney_transaction_enhancer.internet import (
    is_internet_connected,
    wait_for_internet_connection,
)


def test_send_heartbeat_success():
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        send_heartbeat("http://test.com")
        mock_get.assert_called_once_with("http://test.com", timeout=10)


def test_send_heartbeat_failure():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("fail")
        with capture_logs() as cap_logs:
            with pytest.raises(RetryError):
                send_heartbeat("http://test.com")
        assert any("heartbeat failed" in log.get("event", "") for log in cap_logs)


def test_is_internet_connected_true():
    with patch("socket.socket") as mock_sock:
        # Mock the context manager
        mock_sock.return_value.__enter__.return_value.connect.return_value = None
        assert is_internet_connected() is True


def test_is_internet_connected_false():
    with patch("socket.socket") as mock_sock:
        # Use socket.error which is what the code catches
        mock_sock.return_value.__enter__.return_value.connect.side_effect = OSError(
            "no internet"
        )
        assert is_internet_connected() is False


def test_wait_for_internet_connection_immediate():
    with patch(
        "lunchmoney_transaction_enhancer.internet.is_internet_connected"
    ) as mock_check:
        mock_check.return_value = True
        wait_for_internet_connection()
        mock_check.assert_called_once()
