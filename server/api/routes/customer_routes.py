from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from server.schemas.customer import CustomerResponse
from server.services.customer_service import CustomerService
from server.api.dependencies import get_customer_service

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    insurance_agent_id: str = Query(..., description="The ID of the insurance agent"),
    policy_status: Optional[str] = Query(None, description="Filter customers by their policy status"),
    policy_type: Optional[str] = Query(None, description="Filter customers by their policy type"),
    customer_name: Optional[str] = Query(None, description="Filter customers by name (partial match)"),
    customer_service: CustomerService = Depends(get_customer_service)
):
    return customer_service.get_agent_customers(
        agent_id=insurance_agent_id,
        policy_status=policy_status,
        policy_type=policy_type,
        customer_name=customer_name
    )
