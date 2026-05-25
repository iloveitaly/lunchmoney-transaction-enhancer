import re
import structlog
from typing import List, Optional
from pydantic import BaseModel
from whenever import Instant

from lunchable import LunchMoney
from lunchable.models import TransactionObject, TransactionUpdateObject

log = structlog.get_logger()


class ExtractionRule(BaseModel):
    name: str
    source_field: str  # 'payee', 'notes', 'original_name'
    pattern: str  # Regex pattern
    target_field: str  # 'payee', 'notes'
    template: str  # Template for the target field, e.g., "Code: {code}"

    def apply(self, transaction: TransactionObject) -> Optional[dict]:
        source_val = getattr(transaction, self.source_field, None)
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
    def __init__(self, api_token: str, rules: List[ExtractionRule]):
        self.lunch = LunchMoney(access_token=api_token)
        self.rules = rules

    def enhance_transactions(self, start_date: Instant):
        log.info("fetching transactions", start_date=start_date)

        # LunchMoney API uses date, so we'll fetch from the date of start_date
        # Whenever's Instant doesn't have a direct .date() but we can convert
        transactions = self.lunch.get_transactions(
            start_date=start_date.py_datetime().date()
        )

        log.info("fetched transactions", count=len(transactions))

        updated_count = 0
        for tx in transactions:
            updates = {}
            for rule in self.rules:
                result = rule.apply(tx)
                if result:
                    updates.update(result)

            if updates:
                # Check if we are actually changing anything
                is_changed = False
                for field, val in updates.items():
                    current_val = getattr(tx, field, None)
                    if current_val != val:
                        is_changed = True
                        break

                if is_changed:
                    log.info(
                        "updating transaction",
                        id=tx.id,
                        updates=updates,
                        original_payee=tx.payee,
                    )
                    update_obj = TransactionUpdateObject(**updates)
                    self.lunch.update_transaction(tx.id, update_obj)
                    updated_count += 1

        log.info("enhancement complete", updated_count=updated_count)
        return updated_count
