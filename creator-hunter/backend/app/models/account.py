"""
账号管理模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from ..database import Base
from .target import Platform


class AccountStatus(str, enum.Enum):
    """账号状态枚举"""
    ACTIVE = "active"  # 正常使用
    WARNING = "warning"  # 警告状态
    ABNORMAL = "abnormal"  # 异常状态
    DISABLED = "disabled"  # 禁用


import enum


class Account(Base):
    """账号管理表"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    name = Column(String(100), nullable=False, comment="账号名称（备注）")
    platform = Column(SQLEnum(Platform), nullable=False, comment="平台")
    platform_account = Column(String(100), comment="平台账号")

    # 登录信息（加密存储）
    cookies = Column(Text, comment="Cookie信息（加密）")
    login_method = Column(String(50), comment="登录方式（cookie/password/qrcode）")

    # 微信信息
    wechat_id = Column(String(100), comment="对应的微信号")
    operator_name = Column(String(50), comment="运营人员姓名")

    # 限制配置
    daily_limit = Column(Integer, default=50, comment="每日发送上限")
    hourly_limit = Column(Integer, default=30, comment="每小时上限")
    priority = Column(Integer, default=0, comment="优先级")

    # 统计信息
    today_sent_count = Column(Integer, default=0, comment="今日已发送数量")
    total_sent_count = Column(Integer, default=0, comment="总发送数量")
    success_count = Column(Integer, default=0, comment="成功数量")
    failed_count = Column(Integer, default=0, comment="失败数量")
    success_rate = Column(Float, default=1.0, comment="成功率")

    # 健康度
    health_score = Column(Integer, default=100, comment="健康度评分（0-100）")
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.ACTIVE, comment="账号状态")

    # 状态检测
    last_check_time = Column(DateTime(timezone=True), comment="最后检测时间")
    last_error = Column(Text, comment="最后错误信息")

    # 使用状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    is_logged_in = Column(Boolean, default=False, comment="是否已登录")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_used_at = Column(DateTime(timezone=True), comment="最后使用时间")

    def __repr__(self):
        return f"<Account(id={self.id}, name={self.name}, platform={self.platform}, health_score={self.health_score})>"
