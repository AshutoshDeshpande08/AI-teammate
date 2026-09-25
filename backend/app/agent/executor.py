from enum import Enum

from pydantic import BaseModel

from app.agent.decision_engine import Decision
from app.agent.risk_scorer import AutonomyLevel, RiskAssessment
from app.tools.ticket_tool import update_ticket_status


class ExecutionStatus(str, Enum):
    EXECUTED = "executed"
    REQUIRES_APPROVAL = "requires_approval"
    REJECTED = "rejected"


class ExecutionResult(BaseModel):
    status: ExecutionStatus
    action: str
    message: str


def execute_decision(
    decision: Decision,
    risk: RiskAssessment,
) -> ExecutionResult:
    """Execute an AI decision only when the risk gate allows autonomy."""

    if risk.level == AutonomyLevel.HUMAN_APPROVAL:
        return ExecutionResult(
            status=ExecutionStatus.REQUIRES_APPROVAL,
            action=decision.recommended_action.value,
            message="This action requires human approval before execution.",
        )

    if decision.recommended_action.value == "escalate_to_human":
        result = update_ticket_status(
            ticket_id=decision.ticket_id,
            status="escalated",
        )

        if not result.success:
            return ExecutionResult(
                status=ExecutionStatus.REJECTED,
                action=decision.recommended_action.value,
                message=result.message,
            )

        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            action=decision.recommended_action.value,
            message=result.message,
        )

    return ExecutionResult(
        status=ExecutionStatus.REJECTED,
        action=decision.recommended_action.value,
        message=(
            f"Action '{decision.recommended_action.value}' "
            "does not have an executor tool yet."
        ),
    )