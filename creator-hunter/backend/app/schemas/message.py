"""
私信记录 Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..models.message import MessageStatus


class MessageBase(BaseModel):
    """消息基础模型"""
    target_id: int
    template_id: Optional[int] = None
    account_id: int
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """创建消息"""
    task_id: Optional[int] = None


class Message(MessageBase):
    """消息完整模型"""
    id: int
    task_id: Optional[int] = None
    original_template: Optional[str] = None
    status: MessageStatus
    sent_at: Optional[datetime] = None
    viewed_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    reply_content: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageStats(BaseModel):
    """消息统计"""
    total_sent: int
    total_viewed: int
    total_replied: int
    view_rate: float
    reply_rate: float
    avg_reply_time: Optional[float] = None
