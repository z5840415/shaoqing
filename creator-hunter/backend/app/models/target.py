"""
目标创作者模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from ..database import Base
import enum


class Platform(str, enum.Enum):
    """平台枚举"""
    DOUYIN = "douyin"  # 抖音
    XIAOHONGSHU = "xiaohongshu"  # 小红书
    BILIBILI = "bilibili"  # B站
    WECHAT = "wechat"  # 微信


class TargetStatus(str, enum.Enum):
    """目标状态枚举"""
    PENDING = "pending"  # 待联系
    SENT = "sent"  # 已发送
    VIEWED = "viewed"  # 已查看
    REPLIED = "replied"  # 已回复
    ADDED_WECHAT = "added_wechat"  # 已添加微信
    SIGNED = "signed"  # 已签约
    REJECTED = "rejected"  # 已拒绝
    NOT_SUITABLE = "not_suitable"  # 不合适


class Target(Base):
    """目标创作者表"""
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)

    # 基本信息
    nickname = Column(String(100), nullable=False, comment="昵称")
    platform_id = Column(String(100), nullable=False, unique=True, index=True, comment="平台ID（抖音ID等）")
    platform = Column(SQLEnum(Platform), nullable=False, default=Platform.DOUYIN, comment="平台")
    profile_url = Column(String(500), comment="主页链接")

    # 统计信息
    followers_count = Column(Integer, default=0, comment="粉丝数")
    avg_views = Column(Integer, default=0, comment="平均播放量")

    # 标签和备注
    tags = Column(Text, comment="内容标签（JSON）")
    notes = Column(Text, comment="备注信息")

    # 状态信息
    status = Column(SQLEnum(TargetStatus), default=TargetStatus.PENDING, comment="状态")
    priority = Column(Integer, default=0, comment="优先级（数字越大越优先）")

    # 跟进信息
    last_contact_time = Column(DateTime(timezone=True), comment="最后联系时间")
    next_followup_time = Column(DateTime(timezone=True), comment="下次跟进时间")
    contact_count = Column(Integer, default=0, comment="联系次数")

    # 微信信息
    wechat_id = Column(String(100), comment="微信号")
    wechat_added_time = Column(DateTime(timezone=True), comment="添加微信时间")

    # 签约信息
    signed_time = Column(DateTime(timezone=True), comment="签约时间")
    contract_value = Column(Integer, comment="合同金额（元）")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def __repr__(self):
        return f"<Target(id={self.id}, nickname={self.nickname}, platform={self.platform}, status={self.status})>"
