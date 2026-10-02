from typing import List, Optional
import math
from backend.db.repositories.policy_repo import PolicyRepository
from backend.schemas.policy import PolicyResponse
from backend.schemas.pagination import PaginatedResponse

class PolicyService:
    def __init__(self, policy_repo: PolicyRepository):
        self.policy_repo = policy_repo

    def get_agent_policies(
        self, 
        agent_id: str, 
        status: Optional[str] = None, 
        policy_type: Optional[str] = None,
        customer_id: Optional[str] = None,
        search_term: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[PolicyResponse]:
        filters = {}
        if status:
            filters["status"] = status
        if policy_type:
            filters["policy_type"] = policy_type
        if customer_id:
            filters["customer_id"] = customer_id
        if search_term:
            filters["search_term"] = search_term
            
        total_items, policies = self.policy_repo.get_policies_by_agent(agent_id, filters, page, page_size)
        
        results = []
        for p in policies:
            results.append(PolicyResponse(
                id=str(p.get("ID") or p.get("id")),
                policy_number=str(p.get("POLICY_NUMBER") or p.get("policy_number")),
                customer_id=str(p.get("CUSTOMER_ID") or p.get("customer_id")),
                agent_id=str(p.get("AGENT_ID") or p.get("agent_id")),
                policy_type=str(p.get("POLICY_TYPE") or p.get("policy_type")),
                status=str(p.get("STATUS") or p.get("status")),
                start_date=p.get("START_DATE") or p.get("start_date"),
                end_date=p.get("END_DATE") or p.get("end_date"),
                premium_amount=float(p.get("PREMIUM_AMOUNT") or p.get("premium_amount")) if (p.get("PREMIUM_AMOUNT") or p.get("premium_amount")) else None,
                coverage_amount=float(p.get("COVERAGE_AMOUNT") or p.get("coverage_amount")) if (p.get("COVERAGE_AMOUNT") or p.get("coverage_amount")) else None,
            ))
            
        total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
        
        return PaginatedResponse[PolicyResponse](
            total_items=total_items,
            total_pages=total_pages,
            current_page=page,
            count=len(results),
            items=results
        )
