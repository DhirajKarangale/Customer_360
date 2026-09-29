from fastapi import HTTPException, status
from server.schemas.auth import LoginRequest, LoginResponse
from server.db.repositories.agent_repo import AgentRepository
from server.db.repositories.customer_repo import CustomerRepository
import hashlib

class AuthService:
    def __init__(self, agent_repo: AgentRepository, customer_repo: CustomerRepository):
        self.agent_repo = agent_repo
        self.customer_repo = customer_repo

    def authenticate_agent(self, login_data: LoginRequest) -> LoginResponse:
        # Check agent first
        user = self.agent_repo.get_agent_by_email(login_data.email)
        user_type = "agent"
        
        # If not found, check customer
        if not user:
            user = self.customer_repo.get_customer_by_email(login_data.email)
            user_type = "customer"
            
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        db_password = user.get("PASSWORD") or user.get("password")
        
        if db_password is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
            
        hashed_input = hashlib.sha256(login_data.password.encode('utf-8')).hexdigest()
        
        if hashed_input != db_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id = str(user.get("ID") or user.get("id"))
        return LoginResponse(agent_id=user_id, message=f"Login successful as {user_type}")
