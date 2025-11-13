from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== 达人管理相关 ==========
class TargetBase(BaseModel):
    nickname: str = Field(..., description="昵称")
    douyin_id: str = Field(..., description="抖音ID")
    homepage_url: Optional[str] = Field(None, description="主页链接")
    fans_count: int = Field(0, description="粉丝数")
    tags: Optional[str] = Field(None, description="标签")
    notes: Optional[str] = Field(None, description="备注")


class TargetCreate(TargetBase):
    pass


class TargetUpdate(BaseModel):
    nickname: Optional[str] = None
    homepage_url: Optional[str] = None
    fans_count: Optional[int] = None
    tags: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class TargetResponse(TargetBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TargetListResponse(BaseModel):
    total: int
    items: List[TargetResponse]


# ========== 话术模板相关 ==========
class TemplateBase(BaseModel):
    name: str = Field(..., description="话术名称")
    content: str = Field(..., description="话术内容")
    is_default: bool = Field(False, description="是否为默认话术")


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    is_default: Optional[bool] = None


class TemplateResponse(TemplateBase):
    id: int
    usage_count: int
    reply_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== 发送相关 ==========
class SendConfig(BaseModel):
    target_ids: List[int] = Field(..., description="目标达人ID列表")
    template_id: int = Field(..., description="话术模板ID")
    min_interval: int = Field(30, description="最小间隔（秒）")
    max_interval: int = Field(60, description="最大间隔（秒）")
    batch_size: int = Field(30, description="批次大小")
    batch_rest: int = Field(600, description="批次休息时间（秒）")
    daily_limit: int = Field(100, description="每日上限")
    scheduled_time: Optional[datetime] = Field(None, description="定时发送时间")


class SendProgress(BaseModel):
    total: int
    sent: int
    success: int
    failed: int
    remaining: int
    progress: float
    current_target: Optional[str] = None
    estimated_completion: Optional[datetime] = None


class SendResult(BaseModel):
    success: int
    failed: int
    total: int
    failed_reasons: dict


# ========== 发送记录相关 ==========
class SendLogResponse(BaseModel):
    id: int
    target_nickname: str
    template_name: str
    message_content: str
    status: str
    error_message: Optional[str]
    reply_status: str
    reply_content: Optional[str]
    send_time: Optional[datetime]
    reply_time: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 统计相关 ==========
class Statistics(BaseModel):
    today_sent: int
    today_replied: int
    today_reply_rate: float
    week_sent: int
    week_replied: int
    week_reply_rate: float
    month_sent: int
    month_replied: int
    month_reply_rate: float


class TemplateStats(BaseModel):
    template_name: str
    usage_count: int
    reply_count: int
    reply_rate: float


class TimeSlotStats(BaseModel):
    time_slot: str
    reply_count: int
    reply_rate: float


# ========== 设置相关 ==========
class SettingUpdate(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SettingResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Excel导入相关 ==========
class ImportResult(BaseModel):
    success: int
    failed: int
    duplicates: int
    total: int
    errors: List[str] = []
