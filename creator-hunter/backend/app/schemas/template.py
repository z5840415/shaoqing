"""
话术模板 Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.target import Platform


class TemplateBase(BaseModel):
    """话术模板基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    description: Optional[str] = None
    platform: Platform
    scenario: Optional[str] = None
    variables: Optional[str] = None


class TemplateCreate(TemplateBase):
    """创建话术模板"""
    is_default: bool = False


class TemplateUpdate(BaseModel):
    """更新话术模板"""
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    scenario: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    variables: Optional[str] = None


class Template(TemplateBase):
    """话术模板完整模型"""
    id: int
    is_active: bool
    is_default: bool
    usage_count: int
    reply_count: int
    reply_rate: float
    wechat_add_count: int
    wechat_add_rate: float
    ab_test_group: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TemplateStats(BaseModel):
    """话术统计"""
    template_id: int
    template_name: str
    usage_count: int
    reply_rate: float
    wechat_add_rate: float
    avg_reply_time: Optional[float] = None
