from typing import List, Optional
from server.db.repositories.customer_repo import CustomerRepository
from server.schemas.customer import CustomerResponse

class CustomerService:
    def __init__(self, customer_repo: CustomerRepository):
        self.customer_repo = customer_repo

    def get_agent_customers(
        self, 
        agent_id: str, 
        policy_status: Optional[str] = None,
        policy_type: Optional[str] = None,
        customer_name: Optional[str] = None
    ) -> List[CustomerResponse]:
        filters = {}
        if policy_status:
            filters["policy_status"] = policy_status
        if policy_type:
            filters["policy_type"] = policy_type
        if customer_name:
            filters["customer_name"] = customer_name
            
        customers = self.customer_repo.get_customers_by_agent(agent_id, filters)
        
        results = []
        for c in customers:
            results.append(CustomerResponse(
                id=str(c.get("ID") or c.get("id")),
                name=str(c.get("NAME") or c.get("name")),
                email=str(c.get("EMAIL") or c.get("email")),
                phone_number=c.get("PHONE_NUMBER") or c.get("phone_number"),
                date_of_birth=c.get("DATE_OF_BIRTH") or c.get("date_of_birth"),
                address=c.get("ADDRESS") or c.get("address"),
            ))
        return results
