from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import math

router = APIRouter()

INTERCEPT = -6.0
COEFFICIENTS = {
    "age": 0.04,
    "sex_female": 0.5,
    "hair_red": 1.25,
    "sunburns_4+": 0.74,
    "burns_easily": 0.69,
    "moles": 1.10,
    "freckles_many": 0.64,
    "family_history": 0.83,
    "outdoor_activity": 0.6
}
BASELINE_5YR_RISK = 0.003
RACE_MULTIPLIER = {
    "white": 1.0,
    "black": 0.2,
    "asian": 0.3,
    "hispanic": 0.5,
    "other": 0.6
}

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
    race: Optional[str] = None

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

    if input.race:
        race_factor = RACE_MULTIPLIER.get(input.race.lower(), 1.0)
        absolute_risk = relative_risk * BASELINE_5YR_RISK * race_factor
    else:
        absolute_risk = relative_risk * BASELINE_5YR_RISK

    return relative_risk, absolute_risk

@router.post("/calculate-risk")
def calculate_risk(input: RiskInput):
    rel_risk, abs_risk = compute_risk(input)

    message = None
    if input.race is None:
        message = "Note: Race was not specified. Results are based on population-average melanoma incidence."

    return {
        "relative_risk": rel_risk,
        "absolute_5yr_risk": abs_risk,
        "risk_category": (
            "Low" if abs_risk < 0.001 else
            "Moderate" if abs_risk < 0.005 else
            "High"
        ),
        "message": message
    }
