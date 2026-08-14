import datetime
import re

import structlog
from lunchable import LunchMoney
from lunchable.models import TransactionObject, TransactionUpdateObject
from pydantic import BaseModel
from whenever import Instant

log = structlog.get_logger()


class ExtractionRule(BaseModel):
    name: str
    source_field: str  # 'payee', 'notes', 'original_name'
    pattern: str  # Regex pattern
    target_field: str  # 'payee', 'notes'
    template: str  # Template for the target field, e.g., "Code: {code}"

    def _get_source_val(self, transaction: TransactionObject) -> str | None:
        if self.source_field == "plaid_name":
            metadata = transaction.plaid_metadata
            if not metadata:
                return None
            return metadata.get("name")
        return getattr(transaction, self.source_field, None)

    def apply(self, transaction: TransactionObject) -> dict | None:
        source_val = self._get_source_val(transaction)
        if not source_val:
            return None

        match = re.search(self.pattern, source_val)
        if not match:
            return None

        # Use named groups or all groups
        data = match.groupdict()
        if not data and match.groups():
            # If no named groups, use numeric groups
            data = {f"g{i + 1}": g for i, g in enumerate(match.groups())}
            # Also allow just 'match' if only one group
            if len(match.groups()) == 1:
                data["match"] = match.group(1)

        # If no groups at all, use the whole match
        if not data:
            data = {"match": match.group(0)}

        try:
            new_val = self.template.format(**data)
            return {self.target_field: new_val}
        except KeyError as e:
            log.error("template error", rule=self.name, error=str(e), data=data)
            return None


class TransactionEnhancer:
    def __init__(
        self, api_token: str, rules: list[ExtractionRule], dry_run: bool = False
    ):
        self.lunch = LunchMoney(access_token=api_token)
        self.rules = rules
        self.dry_run = dry_run

    def enhance_transactions(self, start_date: Instant):
        log.info("fetching transactions", start_date=start_date)

        # LunchMoney API uses date, so we'll fetch from the date of start_date
        # Whenever's Instant doesn't have a direct .date() but we can convert
        transactions = self.lunch.get_transactions(
            start_date=start_date.py_datetime().date(),
            end_date=datetime.datetime.now(tz=datetime.UTC).date(),
        )

        log.info("fetched transactions", count=len(transactions))

        updated_count = 0
        rule_match_counts = {rule.name: 0 for rule in self.rules}

        for tx in transactions:
            updates = {}
            for rule in self.rules:
                result = rule.apply(tx)
                if result:
                    rule_match_counts[rule.name] += 1
                    updates.update(result)

            if not updates:
                continue

            if "notes" in updates and tx.notes:
                log.warning(
                    "skipping note update because notes are already set",
                    id=tx.id,
                )
                del updates["notes"]

            if not updates:
                continue

            is_changed = any(
                getattr(tx, field, None) != val for field, val in updates.items()
            )
            if not is_changed:
                continue

            log.info(
                "updating transaction",
                id=tx.id,
                updates=updates,
                original_payee=tx.payee,
                dry_run=self.dry_run,
            )
            if not self.dry_run:
                update_obj = TransactionUpdateObject(**updates)
                self.lunch.update_transaction(tx.id, update_obj)
            updated_count += 1

        log.info(
            "enhancement complete",
            updated_count=updated_count,
            rule_matches=rule_match_counts,
        )
        return updated_count
