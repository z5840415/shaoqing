"""
话术模板模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from ..database import Base
from .target import Platform


class Template(Base):
    """话术模板表"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    name = Column(String(100), nullable=False, unique=True, comment="模板名称")
    content = Column(Text, nullable=False, comment="模板内容")
    description = Column(Text, comment="模板描述")

    # 适用信息
    platform = Column(SQLEnum(Platform), nullable=False, comment="适用平台")
    scenario = Column(String(50), comment="适用场景（首次触达/跟进等）")

    # 状态信息
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_default = Column(Boolean, default=False, comment="是否为默认模板")

    # 统计信息
    usage_count = Column(Integer, default=0, comment="使用次数")
    reply_count = Column(Integer, default=0, comment="回复次数")
    reply_rate = Column(Float, default=0.0, comment="回复率")
    wechat_add_count = Column(Integer, default=0, comment="添加微信次数")
    wechat_add_rate = Column(Float, default=0.0, comment="添加微信率")

    # 变量说明
    variables = Column(Text, comment="变量说明（JSON）")

    # A/B测试
    ab_test_group = Column(String(50), comment="A/B测试分组")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_used_at = Column(DateTime(timezone=True), comment="最后使用时间")

    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, platform={self.platform}, reply_rate={self.reply_rate})>"
