from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from backend.schemas.customer import CustomerResponse
from backend.schemas.pagination import PaginatedResponse
from backend.services.customer_service import CustomerService
from backend.api.dependencies import get_customer_service

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", response_model=PaginatedResponse[CustomerResponse])
def get_customers(
    insurance_agent_id: str = Query(..., description="The ID of the insurance agent"),
    policy_status: Optional[str] = Query(None, description="Filter customers by their policy status"),
    policy_type: Optional[str] = Query(None, description="Filter customers by their policy type"),
    customer_name: Optional[str] = Query(None, description="Filter customers by name (partial match)"),
    search_term: Optional[str] = Query(None, description="Search term for name, email, phone, or ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    customer_service: CustomerService = Depends(get_customer_service)
):
    return customer_service.get_agent_customers(
        agent_id=insurance_agent_id,
        policy_status=policy_status,
        policy_type=policy_type,
        customer_name=customer_name,
        search_term=search_term,
        page=page,
        page_size=page_size
    )
