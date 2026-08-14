[![Release Notes](https://img.shields.io/github/release/iloveitaly/lunchmoney-transaction-enhancer)](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/releases)
[![Downloads](https://static.pepy.tech/badge/lunchmoney-transaction-enhancer/month)](https://pepy.tech/project/lunchmoney-transaction-enhancer)
![GitHub CI Status](https://github.com/iloveitaly/lunchmoney-transaction-enhancer/actions/workflows/build_and_publish.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Enrich Lunch Money Transactions with Regex Rules

Applies regex extraction rules to your [Lunch Money](https://lunchmoney.app) transactions to pull structured data out of raw payee names and Plaid metadata. Useful for extracting booking codes, reference numbers, or other patterns that Lunch Money doesn't parse on its own.

## Installation

Run the CLI with `uvx`; it downloads the package automatically when needed.

Set your API key:

```bash
export LUNCH_MONEY_API_KEY=your_token_here
```

## Usage

### Run manually

```bash
uvx lunchmoney-transaction-enhancer
```

### Dry run (no writes)

```bash
uvx lunchmoney-transaction-enhancer --dry-run
```

### Run via cron

```bash
# Ensure HEARTBEAT_URL is set in your environment
uvx lunchmoney-transaction-enhancer --cron
```

### Options

- `--lookback N` — days to look back when no prior state exists (default: 180)
- `--dry-run` — log what would be updated without making any changes
- `--cron` — wait for internet connectivity before running, send heartbeat on success

## Features

- Define regex rules against any transaction field (`payee`, `notes`, `original_name`) or Plaid metadata (`plaid_name`)
- Extract named capture groups and format them into a target field using a template string
- Skips updates when the target field already contains the correct value
- Persists a last-checked timestamp so each run only processes new transactions
- Cron mode waits up to 8 hours for internet connectivity via exponential backoff, then pings a heartbeat URL (compatible with Healthchecks.io, Better Stack, etc.)

## Configuring Rules

Rules are defined in `lunchmoney_transaction_enhancer/config.py`:

```python
ExtractionRule(
    name="Airbnb Code",
    source_field="plaid_name",  # field to match against
    pattern=r"AIRBNB \* (?P<code>[A-Z0-9]{10})",
    target_field="notes",  # field to write to
    template="Airbnb Code: {code}",  # use named capture groups as variables
)
```

## [MIT License](LICENSE.md)

---

*This project was created from [iloveitaly/python-package-template](https://github.com/iloveitaly/python-package-template)*
