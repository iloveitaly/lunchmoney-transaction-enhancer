[![Release Notes](https://img.shields.io/github/release/iloveitaly/lunchmoney-transaction-enhancer)](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/releases)
[![Downloads](https://static.pepy.tech/badge/lunchmoney-transaction-enhancer/month)](https://pepy.tech/project/lunchmoney-transaction-enhancer)
![GitHub CI Status](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/actions/workflows/build_and_publish.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# lunchmoney-transaction-enhancer

## Installation

```bash
uv add lunchmoney-transaction-enhancer
```

## Usage

### Run Manually
```bash
uv run lunchmoney-transaction-enhancer
```

### Run via Cron
```bash
# Ensure HEARTBEAT_URL is set in your environment
uv run lunchmoney-transaction-enhancer --cron
```

## Automated Workflows

### Internet Connection Check
When the `--cron` flag is used, the tool will attempt to verify internet connectivity by connecting to `google.com:80`. It uses an exponential backoff strategy (up to 8 hours) to handle temporary network outages or overnight disconnections.

### Heartbeat Notifications
If the `HEARTBEAT_URL` environment variable is set and the `--cron` flag is used, the tool will send a GET request to the specified URL upon successful completion of the transaction enhancement process. This is compatible with services like [Healthchecks.io](https://healthchecks.io) or [Better Stack](https://betterstack.com).

---

*This project was created from [iloveitaly/python-package-template](https://github.com/iloveitaly/python-package-template)*
