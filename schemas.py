import uuid

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from email_validator import validate_email

class OwnerBase(BaseModel): # Common schema for owner creation and response
    name: str = Field(..., example="John Doe", notnull=True)
    email: str = Field(..., example="john.doe@example.com", notnull=True)
    phone: str = Field(..., example="123-456-7890")

class RegisterOwner(OwnerBase):
    password: str = Field(..., example="securepassword", notnull=True)


class OwnerResponse(OwnerBase):
    
    model_config = ConfigDict(from_attributes=True) # enable Pydentic to read data from ORM models (attributes not only dicts)
     
    id: uuid.UUID 
    created_at: datetime
