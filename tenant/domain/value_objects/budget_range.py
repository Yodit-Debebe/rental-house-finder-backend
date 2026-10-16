from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from ..exceptions import InvalidBudgetRangeException


@dataclass(frozen=True)
class BudgetRange:
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None

    def __post_init__(self):
        min_val = Decimal(str(self.min_price)) if self.min_price is not None else None
        max_val = Decimal(str(self.max_price)) if self.max_price is not None else None

        if min_val is not None and min_val < Decimal("0"):
            raise InvalidBudgetRangeException("Minimum budget cannot be negative.")

        if max_val is not None and max_val < Decimal("0"):
            raise InvalidBudgetRangeException("Maximum budget cannot be negative.")

        if min_val is not None and max_val is not None and min_val > max_val:
            raise InvalidBudgetRangeException(
                f"Minimum budget ({min_val}) cannot be greater than maximum budget ({max_val})."
            )

        object.__setattr__(self, "min_price", min_val)
        object.__setattr__(self, "max_price", max_val)

    def contains(self, price: Decimal | float | int) -> bool:
        p = Decimal(str(price))
        if self.min_price is not None and p < self.min_price:
            return False
        if self.max_price is not None and p > self.max_price:
            return False
        return True

    def is_unbounded(self) -> bool:
        return self.min_price is None and self.max_price is None
