"""
发送任务模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from ..database import Base
import enum


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 待执行
    RUNNING = "running"  # 执行中
    PAUSED = "paused"  # 已暂停
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskType(str, enum.Enum):
    """任务类型枚举"""
    SINGLE = "single"  # 单条发送
    BATCH = "batch"  # 批量发送
    SCHEDULED = "scheduled"  # 定时发送


class Task(Base):
    """发送任务表"""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    # 任务基本信息
    name = Column(String(100), nullable=False, comment="任务名称")
    type = Column(SQLEnum(TaskType), nullable=False, comment="任务类型")
    description = Column(Text, comment="任务描述")

    # 任务配置
    template_id = Column(Integer, comment="使用的模板ID")
    target_ids = Column(Text, comment="目标ID列表（JSON）")

    # 发送策略
    send_mode = Column(String(50), default="immediate", comment="发送方式（immediate/scheduled）")
    scheduled_time = Column(DateTime(timezone=True), comment="定时发送时间")

    # 间隔配置
    interval_min = Column(Integer, default=30, comment="最小间隔（秒）")
    interval_max = Column(Integer, default=90, comment="最大间隔（秒）")

    # 账号策略
    account_rotation = Column(Boolean, default=True, comment="是否账号轮换")
    account_ids = Column(Text, comment="指定账号ID列表（JSON）")

    # 异常处理
    pause_on_error = Column(Boolean, default=True, comment="发送失败时是否暂停")
    auto_pause_after = Column(Integer, default=50, comment="每发送N条后暂停")
    auto_pause_duration = Column(Integer, default=600, comment="暂停时长（秒）")

    # 任务状态
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, comment="任务状态")

    # 统计信息
    total_count = Column(Integer, default=0, comment="总数量")
    sent_count = Column(Integer, default=0, comment="已发送数量")
    success_count = Column(Integer, default=0, comment="成功数量")
    failed_count = Column(Integer, default=0, comment="失败数量")

    # 进度信息
    progress = Column(Integer, default=0, comment="进度百分比")
    current_status = Column(String(200), comment="当前状态描述")
    estimated_completion_time = Column(DateTime(timezone=True), comment="预计完成时间")

    # 时间信息
    started_at = Column(DateTime(timezone=True), comment="开始时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")
    paused_at = Column(DateTime(timezone=True), comment="暂停时间")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name}, status={self.status}, progress={self.progress}%)>"
