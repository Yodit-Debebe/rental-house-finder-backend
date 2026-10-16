import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from tenant.domain.entities import (
    Favorite,
    Inquiry,
    ListingReport,
    Notification,
    TenantProfile,
    VisitRequest,
)
from tenant.domain.enums import (
    InquiryStatus,
    ListingReportStatus,
    NotificationType,
    VisitRequestStatus,
)
from tenant.domain.value_objects import (
    BudgetRange,
    InquiryMessage,
    LocationPreference,
    VisitDate,
)


class TestDomainEntities(unittest.TestCase):
    def test_tenant_profile_creation_and_update(self):
        user_id = uuid4()
        profile = TenantProfile(user_id=user_id)
        self.assertEqual(profile.user_id, user_id)
        self.assertIsNone(profile.preferred_location)
        self.assertIsNone(profile.budget_range)

        # Update budget and location
        profile.set_budget(Decimal("15000"), Decimal("30000"))
        profile.set_location("Addis Ababa", "Bole")

        self.assertIsNotNone(profile.budget_range)
        self.assertEqual(profile.budget_range.min_price, Decimal("15000"))
        self.assertEqual(profile.preferred_location.city, "Addis Ababa")

    def test_favorite_creation(self):
        tenant_id = uuid4()
        property_id = uuid4()
        favorite = Favorite(tenant_id=tenant_id, property_id=property_id)
        self.assertEqual(favorite.tenant_id, tenant_id)
        self.assertEqual(favorite.property_id, property_id)
        self.assertIsNotNone(favorite.id)
        self.assertIsNotNone(favorite.saved_at)

    def test_inquiry_lifecycle(self):
        tenant_id = uuid4()
        property_id = uuid4()
        landlord_id = uuid4()
        msg = InquiryMessage("When can I move in?")
        inquiry = Inquiry(
            tenant_id=tenant_id,
            property_id=property_id,
            landlord_id=landlord_id,
            message=msg,
        )

        self.assertEqual(inquiry.status, InquiryStatus.OPEN)
        self.assertIsNone(inquiry.landlord_reply)

        # Landlord replies
        inquiry.record_reply("You can move in next Monday.")
        self.assertEqual(inquiry.status, InquiryStatus.RESPONDED)
        self.assertEqual(inquiry.landlord_reply, "You can move in next Monday.")
        self.assertIsNotNone(inquiry.replied_at)

        # Close inquiry
        inquiry.close()
        self.assertEqual(inquiry.status, InquiryStatus.CLOSED)

    def test_visit_request_lifecycle(self):
        tenant_id = uuid4()
        property_id = uuid4()
        future_date = VisitDate(datetime.now(timezone.utc) + timedelta(days=3))
        visit = VisitRequest(
            tenant_id=tenant_id,
            property_id=property_id,
            requested_date=future_date,
        )

        self.assertEqual(visit.status, VisitRequestStatus.REQUESTED)
        self.assertTrue(visit.is_pending())

        # Confirm
        visit.confirm(note="See you at 2 PM")
        self.assertEqual(visit.status, VisitRequestStatus.CONFIRMED)
        self.assertEqual(visit.landlord_note, "See you at 2 PM")
        self.assertFalse(visit.is_pending())

        # Complete
        visit.complete()
        self.assertEqual(visit.status, VisitRequestStatus.COMPLETED)

    def test_listing_report_lifecycle(self):
        tenant_id = uuid4()
        property_id = uuid4()
        report = ListingReport(
            tenant_id=tenant_id,
            property_id=property_id,
            reason="Price listed is fraudulent.",
        )
        self.assertEqual(report.status, ListingReportStatus.SUBMITTED)

        report.mark_under_review(notes="Admin checking landlord documents")
        self.assertEqual(report.status, ListingReportStatus.UNDER_REVIEW)

        report.resolve(notes="Listing removed")
        self.assertEqual(report.status, ListingReportStatus.RESOLVED)

    def test_notification_lifecycle(self):
        user_id = uuid4()
        notif = Notification(
            recipient_id=user_id,
            notification_type=NotificationType.INQUIRY_REPLY,
            title="New Reply to your inquiry",
            message="Landlord responded to your question.",
        )
        self.assertFalse(notif.is_read)
        self.assertIsNone(notif.read_at)

        notif.mark_as_read()
        self.assertTrue(notif.is_read)
        self.assertIsNotNone(notif.read_at)


if __name__ == "__main__":
    unittest.main()
