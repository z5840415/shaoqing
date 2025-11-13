"""
发送任务 Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from ..models.task import TaskStatus, TaskType


class TaskBase(BaseModel):
    """任务基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    type: TaskType
    description: Optional[str] = None
    template_id: Optional[int] = None
    target_ids: str  # JSON字符串


class TaskCreate(TaskBase):
    """创建任务"""
    send_mode: str = "immediate"
    scheduled_time: Optional[datetime] = None
    interval_min: int = 30
    interval_max: int = 90
    account_rotation: bool = True
    account_ids: Optional[str] = None
    pause_on_error: bool = True
    auto_pause_after: int = 50
    auto_pause_duration: int = 600


class TaskUpdate(BaseModel):
    """更新任务"""
    status: Optional[TaskStatus] = None
    current_status: Optional[str] = None


class Task(TaskBase):
    """任务完整模型"""
    id: int
    send_mode: str
    scheduled_time: Optional[datetime] = None
    interval_min: int
    interval_max: int
    account_rotation: bool
    account_ids: Optional[str] = None
    pause_on_error: bool
    auto_pause_after: int
    auto_pause_duration: int
    status: TaskStatus
    total_count: int
    sent_count: int
    success_count: int
    failed_count: int
    progress: int
    current_status: Optional[str] = None
    estimated_completion_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskProgress(BaseModel):
    """任务进度"""
    task_id: int
    task_name: str
    status: TaskStatus
    progress: int
    sent_count: int
    success_count: int
    failed_count: int
    total_count: int
    current_status: Optional[str] = None
    estimated_completion_time: Optional[datetime] = None
