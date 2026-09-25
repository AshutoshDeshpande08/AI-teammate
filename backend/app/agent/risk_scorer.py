from enum import Enum

from pydantic import BaseModel

from app.agent.decision_engine import Decision


class AutonomyLevel(str, Enum):
    AUTO = "auto"
    HUMAN_APPROVAL = "human_approval"


class RiskAssessment(BaseModel):
    level: AutonomyLevel
    risk_score: int
    reasons: list[str]

def assess_risk(decision: Decision) -> RiskAssessment:
    """Apply deterministic safety rules to an AI-generated decision."""

    reasons: list[str] = []
    risk_score = 0

    if decision.requires_human:
        risk_score += 50
        reasons.append("The AI decision already requires human approval.")

    if decision.urgency.value == "urgent":
        risk_score += 30
        reasons.append("The ticket is marked as urgent.")

    elif decision.urgency.value == "high":
        risk_score += 15
        reasons.append("The ticket is marked as high urgency.")

    if decision.recommended_action.value in {
        "issue_refund",
        "update_account",
    }:
        risk_score += 25
        reasons.append(
            "The recommended action changes customer data or financial state."
        )

    if decision.recommended_action.value == "escalate_to_human":
        risk_score += 40
        reasons.append("The AI recommends escalation to a human.")

    if risk_score >= 50:
        level = AutonomyLevel.HUMAN_APPROVAL
    else:
        level = AutonomyLevel.AUTO

    return RiskAssessment(
        level=level,
        risk_score=min(risk_score, 100),
        reasons=reasons,
    )