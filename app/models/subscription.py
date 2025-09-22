from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SubscriptionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class SubscriptionRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    organization: Optional[str] = None
    interests: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class SubscriptionResponse(BaseModel):
    request_id: str
    status: str
    message: str


class Subscription(BaseModel):
    request_id: str
    email: str
    name: Optional[str] = None
    organization: Optional[str] = None
    interests: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None
    status: SubscriptionStatus = SubscriptionStatus.PENDING
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AdminLoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str