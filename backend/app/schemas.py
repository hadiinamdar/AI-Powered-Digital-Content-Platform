from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    full_name: str
    email: EmailStr
    organization: Optional[str] = None
    password: str = Field(min_length=8)


class SignupOut(BaseModel):
    message: str
    dev_otp: Optional[str] = None


class VerifyOtpIn(BaseModel):
    email: EmailStr
    code: str


class ResendOtpIn(BaseModel):
    email: EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str


class GenerateIn(BaseModel):
    prompt: str
    content_type: str = "Poster"
    style: str = "Modern"
    aspect_ratio: str = "1:1 (Square)"
    color_theme: str = "Blue"


class ContentOut(BaseModel):
    id: str
    content_type: str
    style: str
    aspect_ratio: str
    color_theme: str
    prompt: str
    caption: Optional[str]
    status: str
    admin_comment: Optional[str]
    owner_id: str
    owner_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DecisionIn(BaseModel):
    decision: str  # "approved" | "rejected"
    comment: Optional[str] = None


class CommentIn(BaseModel):
    body: str


class CommentOut(BaseModel):
    id: str
    author_role: str
    body: str
    created_at: datetime

    class Config:
        from_attributes = True


class PublishIn(BaseModel):
    platforms: List[str]
    schedule_at: Optional[datetime] = None


class PublishResultItem(BaseModel):
    platform: str
    status: str
    external_post_id: Optional[str] = None
    error: Optional[str] = None


class PublishOut(BaseModel):
    content_id: str
    results: List[PublishResultItem]
