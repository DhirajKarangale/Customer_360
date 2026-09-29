from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from server.schemas.policy import PolicyResponse
from server.services.policy_service import PolicyService
from server.api.dependencies import get_policy_service

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("/", response_model=List[PolicyResponse])
def get_policies(
    insurance_agent_id: str = Query(..., description="The ID of the insurance agent"),
    status: Optional[str] = Query(None, description="Filter by policy status"),
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    return policy_service.get_agent_policies(
        agent_id=insurance_agent_id,
        status=status,
        policy_type=policy_type
    )
