from fastapi import APIRouter
from pydantic import BaseModel
import math

router = APIRouter()

INTERCEPT = -6.0
COEFFICIENTS = { ... }  # same as before
BASELINE_5YR_RISK = 0.003

class RiskInput(BaseModel):
    user_id: str
    age: int
    sex: str
    hair_color: str
    sunburns: int
    burns_easily: bool
    moles: bool
    freckles: str
    family_history: bool
    outdoor_activity: str

def compute_risk(input: RiskInput):
    logit = INTERCEPT
    logit += COEFFICIENTS["age"] * input.age
    logit += COEFFICIENTS["sex_female"] if input.sex == "female" else 0
    logit += COEFFICIENTS["hair_red"] if input.hair_color == "red" else 0
    logit += COEFFICIENTS["sunburns_4+"] if input.sunburns >= 4 else 0
    logit += COEFFICIENTS["burns_easily"] if input.burns_easily else 0
    logit += COEFFICIENTS["moles"] if input.moles else 0
    logit += COEFFICIENTS["freckles_many"] if input.freckles == "many" else 0
    logit += COEFFICIENTS["family_history"] if input.family_history else 0
    logit += COEFFICIENTS["outdoor_activity"] if input.outdoor_activity == "mostly_outdoors" else 0

    relative_risk = 1 / (1 + math.exp(-logit))
    absolute_risk = relative_risk * BASELINE_5YR_RISK
    return relative_risk, absolute_risk

@router.post("/calculate-risk")
def calculate_risk(input: RiskInput):
    rel_risk, abs_risk = compute_risk(input)
    return {
        "relative_risk": rel_risk,
        "absolute_5yr_risk": abs_risk,
        "risk_category": (
            "Low" if abs_risk < 0.001 else
            "Moderate" if abs_risk < 0.005 else
            "High"
        )
    }
