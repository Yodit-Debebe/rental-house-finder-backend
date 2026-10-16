import unittest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from tenant.domain.entities import VisitRequest
from tenant.domain.enums import VisitRequestStatus
from tenant.domain.exceptions import DuplicateVisitRequestException
from tenant.domain.services import VisitEligibilityService
from tenant.domain.value_objects import VisitDate


class TestDomainServices(unittest.TestCase):
    def test_visit_eligibility_prevents_duplicate_pending(self):
        tenant_id = uuid4()
        property_id = uuid4()
        date1 = VisitDate(datetime.now(timezone.utc) + timedelta(days=2))
        date2 = VisitDate(datetime.now(timezone.utc) + timedelta(days=5))

        existing_req = VisitRequest(
            tenant_id=tenant_id,
            property_id=property_id,
            requested_date=date1,
            status=VisitRequestStatus.REQUESTED,
        )

        with self.assertRaises(DuplicateVisitRequestException):
            VisitEligibilityService.ensure_can_request_visit(
                existing_requests=[existing_req],
                tenant_id=tenant_id,
                property_id=property_id,
                requested_date=date2,
            )

    def test_visit_eligibility_allows_if_previous_completed_or_declined(self):
        tenant_id = uuid4()
        property_id = uuid4()
        date1 = VisitDate(datetime.now(timezone.utc) + timedelta(days=2))
        date2 = VisitDate(datetime.now(timezone.utc) + timedelta(days=5))

        completed_req = VisitRequest(
            tenant_id=tenant_id,
            property_id=property_id,
            requested_date=date1,
            status=VisitRequestStatus.COMPLETED,
        )

        # Should not raise exception
        VisitEligibilityService.ensure_can_request_visit(
            existing_requests=[completed_req],
            tenant_id=tenant_id,
            property_id=property_id,
            requested_date=date2,
        )


if __name__ == "__main__":
    unittest.main()
