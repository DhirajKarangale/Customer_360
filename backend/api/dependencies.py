from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import psycopg2.extensions
from backend.db.connection import get_db_connection
from backend.utils.jwt_utils import verify_token
from backend.db.repositories.agent_repo import AgentRepository
from backend.db.repositories.policy_repo import PolicyRepository
from backend.db.repositories.customer_repo import CustomerRepository
from backend.services.auth_service import AuthService
from backend.services.agent_service import AgentService
from backend.services.policy_service import PolicyService
from backend.services.customer_service import CustomerService
from backend.services.llm_service import LLMService

def get_agent_repo(conn: psycopg2.extensions.connection = Depends(get_db_connection)) -> AgentRepository:
    return AgentRepository(conn)

def get_policy_repo(conn: psycopg2.extensions.connection = Depends(get_db_connection)) -> PolicyRepository:
    return PolicyRepository(conn)

def get_customer_repo(conn: psycopg2.extensions.connection = Depends(get_db_connection)) -> CustomerRepository:
    return CustomerRepository(conn)

def get_auth_service(
    agent_repo: AgentRepository = Depends(get_agent_repo)
) -> AuthService:
    return AuthService(agent_repo)

def get_agent_service(agent_repo: AgentRepository = Depends(get_agent_repo)) -> AgentService:
    return AgentService(agent_repo)

def get_policy_service(policy_repo: PolicyRepository = Depends(get_policy_repo)) -> PolicyService:
    return PolicyService(policy_repo)

def get_customer_service(customer_repo: CustomerRepository = Depends(get_customer_repo)) -> CustomerService:
    return CustomerService(customer_repo)

def get_llm_service() -> LLMService:
    return LLMService()

security = HTTPBearer()

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload
