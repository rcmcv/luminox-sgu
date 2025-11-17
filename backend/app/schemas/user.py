from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class UserBase(BaseModel):
    email: str = Field(..., max_length=180)      # pode trocar por EmailStr depois
    full_name: str = Field(..., max_length=120)
    role: str = Field(default="VIEWER")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginInput(BaseModel):
    email: str
    password: str

class UserUpdateSelf(BaseModel):
    full_name: Optional[str] = Field(None, max_length=120)
    email: Optional[str] = Field(None, max_length=180)

class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = Field(None, max_length=120)
    email: Optional[str] = Field(None, max_length=180)
    role: Optional[str] = Field(None)          # ADMIN, FINANCE, OPERACAO, VIEWER
    is_active: Optional[bool] = None

class PasswordChangeSelf(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)

class PasswordSetAdmin(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128)
