from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

class OperationType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class BudgetPeriod(str, Enum):
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CurrencyBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=3)
    name: str = Field(..., max_length=50)

class CurrencyResponse(CurrencyBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class AccountBase(BaseModel):
    name: str = Field(..., max_length=100)
    balance: Decimal = Field(default=0.00, ge=0)
    is_active: bool = Field(default=True)

class AccountCreate(AccountBase):
    currency_id: int

class AccountResponse(AccountBase):
    id: int
    user_id: int
    currency_id: int
    created_at: datetime
    currency: Optional[CurrencyResponse] = None
    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: OperationType
    is_active: bool = Field(default=True)

class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None

class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    parent_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class TransactionBase(BaseModel):
    amount: Decimal
    description: Optional[str] = None
    date: Optional[datetime] = None

class TransactionCreate(TransactionBase):
    account_id: int
    category_id: int

class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    account_id: int
    category_id: int
    created_at: datetime
    account: Optional[AccountResponse] = None
    category: Optional[CategoryResponse] = None
    model_config = ConfigDict(from_attributes=True)

class BudgetBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    period: BudgetPeriod
    start_date: date
    end_date: date

class BudgetCreate(BudgetBase):
    category_id: int

class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    category_id: int
    created_at: datetime
    category: Optional[CategoryResponse] = None
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None