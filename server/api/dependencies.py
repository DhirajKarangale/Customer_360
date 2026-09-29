from fastapi import Depends
import psycopg2.extensions
from server.db.connection import get_db_connection
from server.db.repositories.agent_repo import AgentRepository
from server.db.repositories.policy_repo import PolicyRepository
from server.db.repositories.customer_repo import CustomerRepository
from server.services.auth_service import AuthService
from server.services.agent_service import AgentService
from server.services.policy_service import PolicyService
from server.services.customer_service import CustomerService
from server.services.llm_service import LLMService

def get_agent_repo(conn: psycopg2.extensions.connection = Depends(get_db_connection)) -> AgentRepository:
    return AgentRepository(conn)

def get_policy_repo(conn: psycopg2.extensions.connection = Depends(get_db_connection)) -> PolicyRepository:
    return PolicyRepository(conn)

def get_customer_repo(conn: psycopg2.extensions.connection = Depends(get_db_connection)) -> CustomerRepository:
    return CustomerRepository(conn)

def get_auth_service(
    agent_repo: AgentRepository = Depends(get_agent_repo),
    customer_repo: CustomerRepository = Depends(get_customer_repo)
) -> AuthService:
    return AuthService(agent_repo, customer_repo)

def get_agent_service(agent_repo: AgentRepository = Depends(get_agent_repo)) -> AgentService:
    return AgentService(agent_repo)

def get_policy_service(policy_repo: PolicyRepository = Depends(get_policy_repo)) -> PolicyService:
    return PolicyService(policy_repo)

def get_customer_service(customer_repo: CustomerRepository = Depends(get_customer_repo)) -> CustomerService:
    return CustomerService(customer_repo)

def get_llm_service() -> LLMService:
    return LLMService()
