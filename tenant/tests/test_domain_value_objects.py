import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from tenant.domain.exceptions import (
    EmptyInquiryMessageException,
    InvalidBudgetRangeException,
    InvalidLocationPreferenceException,
    InvalidVisitDateException,
)
from tenant.domain.value_objects import (
    BudgetRange,
    InquiryMessage,
    LocationPreference,
    VisitDate,
)


class TestDomainValueObjects(unittest.TestCase):
    # BudgetRange Tests
    def test_valid_budget_range(self):
        budget = BudgetRange(min_price=Decimal("10000"), max_price=Decimal("25000"))
        self.assertEqual(budget.min_price, Decimal("10000"))
        self.assertEqual(budget.max_price, Decimal("25000"))
        self.assertTrue(budget.contains(15000))
        self.assertFalse(budget.contains(5000))
        self.assertFalse(budget.contains(30000))

    def test_budget_range_min_greater_than_max_raises(self):
        with self.assertRaises(InvalidBudgetRangeException):
            BudgetRange(min_price=Decimal("30000"), max_price=Decimal("20000"))

    def test_budget_range_negative_raises(self):
        with self.assertRaises(InvalidBudgetRangeException):
            BudgetRange(min_price=Decimal("-100"), max_price=Decimal("20000"))

        with self.assertRaises(InvalidBudgetRangeException):
            BudgetRange(min_price=Decimal("100"), max_price=Decimal("-500"))

    def test_unbounded_budget_range(self):
        budget = BudgetRange()
        self.assertTrue(budget.is_unbounded())
        self.assertTrue(budget.contains(50000))

    # VisitDate Tests
    def test_valid_future_visit_date(self):
        future = datetime.now(timezone.utc) + timedelta(days=2)
        visit_date = VisitDate(future)
        self.assertEqual(visit_date.value, future)

    def test_past_visit_date_raises(self):
        past = datetime.now(timezone.utc) - timedelta(days=1)
        with self.assertRaises(InvalidVisitDateException):
            VisitDate(past)

    # InquiryMessage Tests
    def test_valid_inquiry_message(self):
        msg = InquiryMessage("   Is this property still available?   ")
        self.assertEqual(msg.content, "Is this property still available?")

    def test_empty_inquiry_message_raises(self):
        with self.assertRaises(EmptyInquiryMessageException):
            InquiryMessage("   ")

        with self.assertRaises(EmptyInquiryMessageException):
            InquiryMessage("hi")  # less than 3 chars

    def test_too_long_inquiry_message_raises(self):
        with self.assertRaises(EmptyInquiryMessageException):
            InquiryMessage("a" * 2001)

    # LocationPreference Tests
    def test_valid_location_preference(self):
        loc = LocationPreference(city="Addis Ababa", area="Bole")
        self.assertEqual(loc.city, "Addis Ababa")
        self.assertEqual(loc.area, "Bole")
        self.assertEqual(str(loc), "Bole, Addis Ababa")
        self.assertTrue(loc.matches("Addis Ababa", "Bole Medhanialem"))
        self.assertFalse(loc.matches("Hawassa", "Bole"))

    def test_empty_city_raises(self):
        with self.assertRaises(InvalidLocationPreferenceException):
            LocationPreference(city="   ", area="Bole")


if __name__ == "__main__":
    unittest.main()
