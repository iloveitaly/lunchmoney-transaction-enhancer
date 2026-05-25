from unittest.mock import patch

import pytest
from click.testing import CliRunner
from structlog.testing import capture_logs

from lunchmoney_transaction_enhancer.cli import main_cmd


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_basic_run(runner):
    with patch(
        "lunchmoney_transaction_enhancer.cli.TransactionEnhancer"
    ) as mock_enhancer:
        mock_enhancer_inst = mock_enhancer.return_value
        mock_enhancer_inst.enhance_transactions.return_value = 5

        result = runner.invoke(main_cmd, ["--token", "fake_token", "--lookback", "5"])

        assert result.exit_code == 0
        mock_enhancer.assert_called_once()
        mock_enhancer_inst.enhance_transactions.assert_called_once()


def test_cli_cron_mode(runner):
    with patch("lunchmoney_transaction_enhancer.cli.TransactionEnhancer"):
        with patch(
            "lunchmoney_transaction_enhancer.cli.wait_for_internet_connection"
        ) as mock_wait:
            with patch(
                "lunchmoney_transaction_enhancer.cli.send_heartbeat"
            ) as mock_heartbeat:
                with patch(
                    "lunchmoney_transaction_enhancer.cli.HEARTBEAT_URL",
                    "http://heartbeat.com",
                ):
                    result = runner.invoke(main_cmd, ["--token", "fake", "--cron"])

                    assert result.exit_code == 0
                    mock_wait.assert_called_once()
                    mock_heartbeat.assert_called_once_with("http://heartbeat.com")


def test_cli_missing_token(runner):
    with capture_logs() as cap_logs:
        runner.invoke(main_cmd, ["--token", ""])
    assert any(
        "lunchmoney_api_token is not set" in log.get("event", "")
        for log in cap_logs
    )


def test_cli_error_handling(runner):
    with patch(
        "lunchmoney_transaction_enhancer.cli.TransactionEnhancer"
    ) as mock_enhancer:
        mock_enhancer_inst = mock_enhancer.return_value
        mock_enhancer_inst.enhance_transactions.side_effect = Exception("api error")

        # Test non-cron mode doesn't raise
        result = runner.invoke(main_cmd, ["--token", "fake"])
        assert result.exit_code == 0

        # Test cron mode raises
        result = runner.invoke(main_cmd, ["--token", "fake", "--cron"])
        assert result.exit_code != 0
