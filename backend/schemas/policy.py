from pydantic import BaseModel
from typing import Optional
from datetime import date


class PolicyResponse(BaseModel):
    id: str
    policy_number: str
    customer_id: str
    agent_id: str
    policy_type: str
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    premium_amount: Optional[float] = None
    coverage_amount: Optional[float] = None
