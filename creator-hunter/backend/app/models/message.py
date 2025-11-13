"""
私信记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class MessageStatus(str, enum.Enum):
    """消息状态枚举"""
    PENDING = "pending"  # 待发送
    SENDING = "sending"  # 发送中
    SENT = "sent"  # 已发送
    FAILED = "failed"  # 发送失败
    VIEWED = "viewed"  # 已查看
    REPLIED = "replied"  # 已回复


class Message(Base):
    """私信记录表"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    # 关联信息
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False, comment="目标创作者ID")
    template_id = Column(Integer, ForeignKey("templates.id"), comment="话术模板ID")
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, comment="发送账号ID")
    task_id = Column(Integer, ForeignKey("tasks.id"), comment="所属任务ID")

    # 消息内容
    content = Column(Text, nullable=False, comment="消息内容")
    original_template = Column(Text, comment="原始模板内容")

    # 状态信息
    status = Column(SQLEnum(MessageStatus), default=MessageStatus.PENDING, comment="消息状态")

    # 发送信息
    sent_at = Column(DateTime(timezone=True), comment="发送时间")
    viewed_at = Column(DateTime(timezone=True), comment="查看时间")
    replied_at = Column(DateTime(timezone=True), comment="回复时间")

    # 回复内容
    reply_content = Column(Text, comment="回复内容")

    # 错误信息
    error_message = Column(Text, comment="错误信息")
    retry_count = Column(Integer, default=0, comment="重试次数")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Message(id={self.id}, target_id={self.target_id}, status={self.status})>"
