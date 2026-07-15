from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re

# --- 인증 스키마 ---
class UserSignUp(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

# --- 카테고리 스키마 ---
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=10, description="카테고리명 최소 1자, 최대 10자")

class CategoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    class Config:
        from_attributes = True

# --- 연락처 스키마 ---
class ContactCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=1, max_length=5, description="이름 최소 1자, 최대 5자")
    phone: str = Field(..., description="010으로 시작하는 총 11자리 숫자")
    addr: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^010\d{8}$", v):
            raise ValueError("전화번호 형식은 반드시 010으로 시작하는 11자리 숫자여야 합니다.")
        return v

class ContactUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=1, max_length=5)
    phone: Optional[str] = None
    addr: Optional[str] = None

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^010\d{8}$", v):
            raise ValueError("전화번호 형식은 반드시 010으로 시작하는 11자리 숫자여야 합니다.")
        return v

class ContactResponse(BaseModel):
    id: int
    user_id: int
    category_id: int
    name: str
    phone: str
    addr: Optional[str]
    class Config:
        from_attributes = True