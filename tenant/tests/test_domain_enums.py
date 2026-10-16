import unittest
from tenant.domain.enums import (
    VisitRequestStatus,
    InquiryStatus,
    ListingReportStatus,
    NotificationType,
)


class TestDomainEnums(unittest.TestCase):
    def test_visit_request_status_values(self):
        self.assertEqual(VisitRequestStatus.REQUESTED.value, "requested")
        self.assertEqual(VisitRequestStatus.CONFIRMED.value, "confirmed")
        self.assertEqual(VisitRequestStatus.DECLINED.value, "declined")
        self.assertEqual(VisitRequestStatus.COMPLETED.value, "completed")
        self.assertEqual(VisitRequestStatus.CANCELLED.value, "cancelled")

    def test_inquiry_status_values(self):
        self.assertEqual(InquiryStatus.OPEN.value, "open")
        self.assertEqual(InquiryStatus.RESPONDED.value, "responded")
        self.assertEqual(InquiryStatus.CLOSED.value, "closed")

    def test_listing_report_status_values(self):
        self.assertEqual(ListingReportStatus.SUBMITTED.value, "submitted")
        self.assertEqual(ListingReportStatus.UNDER_REVIEW.value, "under_review")
        self.assertEqual(ListingReportStatus.RESOLVED.value, "resolved")
        self.assertEqual(ListingReportStatus.DISMISSED.value, "dismissed")

    def test_notification_type_values(self):
        self.assertEqual(NotificationType.INQUIRY_REPLY.value, "inquiry_reply")
        self.assertEqual(NotificationType.VISIT_UPDATE.value, "visit_update")
        self.assertEqual(NotificationType.PRICE_CHANGE.value, "price_change")


if __name__ == "__main__":
    unittest.main()
