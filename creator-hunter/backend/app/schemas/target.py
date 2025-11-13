"""
目标创作者 Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.target import Platform, TargetStatus


class TargetBase(BaseModel):
    """目标创作者基础模型"""
    nickname: str = Field(..., min_length=1, max_length=100)
    platform_id: str = Field(..., min_length=1, max_length=100)
    platform: Platform = Platform.DOUYIN
    profile_url: Optional[str] = None
    followers_count: int = 0
    avg_views: int = 0
    tags: Optional[str] = None
    notes: Optional[str] = None
    priority: int = 0


class TargetCreate(TargetBase):
    """创建目标创作者"""
    pass


class TargetUpdate(BaseModel):
    """更新目标创作者"""
    nickname: Optional[str] = None
    profile_url: Optional[str] = None
    followers_count: Optional[int] = None
    avg_views: Optional[int] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[TargetStatus] = None
    priority: Optional[int] = None
    wechat_id: Optional[str] = None


class Target(TargetBase):
    """目标创作者完整模型"""
    id: int
    status: TargetStatus
    last_contact_time: Optional[datetime] = None
    next_followup_time: Optional[datetime] = None
    contact_count: int
    wechat_id: Optional[str] = None
    wechat_added_time: Optional[datetime] = None
    signed_time: Optional[datetime] = None
    contract_value: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TargetImport(BaseModel):
    """批量导入目标创作者"""
    targets: List[TargetCreate]


class TargetFilter(BaseModel):
    """目标筛选条件"""
    status: Optional[TargetStatus] = None
    platform: Optional[Platform] = None
    followers_min: Optional[int] = None
    followers_max: Optional[int] = None
    tags: Optional[str] = None
    search: Optional[str] = None
