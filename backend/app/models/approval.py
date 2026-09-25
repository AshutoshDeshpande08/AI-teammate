from enum import Enum

from pydantic import BaseModel


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(BaseModel):
    ticket_id: int
    action: str
    reason: str
    risk_score: int
    status: ApprovalStatus = ApprovalStatus.PENDING