from typing import Sequence
from uuid import UUID

from ..entities import VisitRequest
from ..enums import VisitRequestStatus
from ..exceptions import DuplicateVisitRequestException
from ..value_objects import VisitDate


class VisitEligibilityService:
    """Domain service to enforce business invariants across visit requests."""

    @staticmethod
    def ensure_can_request_visit(
        existing_requests: Sequence[VisitRequest],
        tenant_id: UUID,
        property_id: UUID,
        requested_date: VisitDate,
    ) -> None:
        """
        Enforces UC-T-09 invariant:
        If a duplicate pending request exists, the system prevents duplicate submission.
        """
        for req in existing_requests:
            if (
                req.tenant_id == tenant_id
                and req.property_id == property_id
                and req.status in (VisitRequestStatus.REQUESTED, VisitRequestStatus.CONFIRMED)
            ):
                raise DuplicateVisitRequestException(
                    "A pending or confirmed visit request already exists for this property."
                )
