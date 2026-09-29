from pydantic import BaseModel
from typing import Optional
from datetime import date

class CustomerResponse(BaseModel):
    id: str
    name: str
    email: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
