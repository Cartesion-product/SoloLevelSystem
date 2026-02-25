"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    settings: dict

    model_config = {"from_attributes": True}


class UserSettingsUpdate(BaseModel):
    auto_update_knowledge: bool | None = None
    default_resume_id: str | None = None
    default_job_id: str | None = None
