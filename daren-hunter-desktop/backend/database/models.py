from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Target(Base):
    """达人信息表"""
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(100), nullable=False, comment="昵称")
    douyin_id = Column(String(100), unique=True, nullable=False, index=True, comment="抖音ID")
    homepage_url = Column(String(500), comment="主页链接")
    fans_count = Column(Integer, default=0, comment="粉丝数")
    tags = Column(String(200), comment="标签，逗号分隔")
    status = Column(String(50), default="pending", comment="状态：pending待发送, sent已发送, replied已回复, wechat已加微信, signed已签约, rejected已拒绝")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class Template(Base):
    """话术模板表"""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="话术名称")
    content = Column(Text, nullable=False, comment="话术内容")
    is_default = Column(Boolean, default=False, comment="是否为默认话术")
    usage_count = Column(Integer, default=0, comment="使用次数")
    reply_count = Column(Integer, default=0, comment="回复次数")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class SendLog(Base):
    """发送记录表"""
    __tablename__ = "send_logs"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, nullable=False, index=True, comment="达人ID")
    target_nickname = Column(String(100), comment="达人昵称（冗余字段）")
    template_id = Column(Integer, comment="话术模板ID")
    template_name = Column(String(100), comment="话术名称（冗余字段）")
    message_content = Column(Text, comment="实际发送的消息内容")
    status = Column(String(50), comment="发送状态：success成功, failed失败, pending待发送")
    error_message = Column(Text, comment="错误信息")
    reply_status = Column(String(50), default="waiting", comment="回复状态：waiting待查看, replied已回复, ignored已忽略")
    reply_content = Column(Text, comment="回复内容")
    send_time = Column(DateTime, comment="发送时间")
    reply_time = Column(DateTime, comment="回复时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class Setting(Base):
    """系统设置表"""
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True, comment="设置键")
    value = Column(Text, comment="设置值（JSON格式）")
    description = Column(String(200), comment="设置说明")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
