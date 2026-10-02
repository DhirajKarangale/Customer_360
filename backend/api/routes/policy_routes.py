from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from backend.schemas.policy import PolicyResponse
from backend.schemas.pagination import PaginatedResponse
from backend.services.policy_service import PolicyService
from backend.api.dependencies import get_policy_service

router = APIRouter(prefix="/policies", tags=["Policies"])

@router.get("/", response_model=PaginatedResponse[PolicyResponse])
def get_policies(
    insurance_agent_id: str = Query(..., description="The ID of the insurance agent"),
    status: Optional[str] = Query(None, description="Filter by policy status"),
    policy_type: Optional[str] = Query(None, description="Filter by policy type"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    search_term: Optional[str] = Query(None, description="Search term for ID, agent ID, customer ID, or policy number"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    policy_service: PolicyService = Depends(get_policy_service)
):
    return policy_service.get_agent_policies(
        agent_id=insurance_agent_id,
        status=status,
        policy_type=policy_type,
        customer_id=customer_id,
        search_term=search_term,
        page=page,
        page_size=page_size
    )
