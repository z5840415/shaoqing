"""
账号管理 Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.target import Platform
from ..models.account import AccountStatus


class AccountBase(BaseModel):
    """账号基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    platform: Platform
    platform_account: Optional[str] = None
    wechat_id: Optional[str] = None
    operator_name: Optional[str] = None
    daily_limit: int = 50
    hourly_limit: int = 30
    priority: int = 0


class AccountCreate(AccountBase):
    """创建账号"""
    cookies: Optional[str] = None
    login_method: str = "cookie"


class AccountUpdate(BaseModel):
    """更新账号"""
    name: Optional[str] = None
    cookies: Optional[str] = None
    wechat_id: Optional[str] = None
    operator_name: Optional[str] = None
    daily_limit: Optional[int] = None
    hourly_limit: Optional[int] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None


class Account(AccountBase):
    """账号完整模型"""
    id: int
    login_method: str
    today_sent_count: int
    total_sent_count: int
    success_count: int
    failed_count: int
    success_rate: float
    health_score: int
    status: AccountStatus
    is_active: bool
    is_logged_in: bool
    last_check_time: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccountHealth(BaseModel):
    """账号健康度"""
    account_id: int
    account_name: str
    health_score: int
    status: AccountStatus
    success_rate: float
    today_sent: int
    daily_limit: int
    recommendations: list[str] = []
