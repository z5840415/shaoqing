"""
消息管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Message, MessageStatus, Target, Template, Account
from ..schemas import (
    Message as MessageSchema,
    MessageCreate,
    MessageStats
)

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/", response_model=MessageSchema)
def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """创建消息记录"""
    db_message = Message(**message.model_dump())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/", response_model=List[MessageSchema])
def list_messages(
    skip: int = 0,
    limit: int = 100,
    status: Optional[MessageStatus] = None,
    target_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取消息列表"""
    query = db.query(Message)

    if status:
        query = query.filter(Message.status == status)
    if target_id:
        query = query.filter(Message.target_id == target_id)

    messages = query.order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    return messages


@router.get("/{message_id}", response_model=MessageSchema)
def get_message(message_id: int, db: Session = Depends(get_db)):
    """获取单个消息"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")
    return message


@router.put("/{message_id}/status")
def update_message_status(
    message_id: int,
    status: MessageStatus,
    reply_content: Optional[str] = None,
    error_message: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """更新消息状态"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="消息不存在")

    message.status = status

    if status == MessageStatus.SENT:
        message.sent_at = datetime.now()
    elif status == MessageStatus.VIEWED:
        message.viewed_at = datetime.now()
    elif status == MessageStatus.REPLIED:
        message.replied_at = datetime.now()
        if reply_content:
            message.reply_content = reply_content

        # 更新目标状态
        target = db.query(Target).filter(Target.id == message.target_id).first()
        if target:
            from ..models.target import TargetStatus
            target.status = TargetStatus.REPLIED

        # 更新模板统计
        if message.template_id:
            template = db.query(Template).filter(Template.id == message.template_id).first()
            if template:
                template.reply_count += 1
                template.reply_rate = template.reply_count / template.usage_count if template.usage_count > 0 else 0

    elif status == MessageStatus.FAILED:
        if error_message:
            message.error_message = error_message
        message.retry_count += 1

    db.commit()
    db.refresh(message)
    return message


@router.get("/stats/overview", response_model=MessageStats)
def get_message_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """获取消息统计概览"""
    query = db.query(Message)

    if start_date:
        query = query.filter(Message.created_at >= start_date)
    if end_date:
        query = query.filter(Message.created_at <= end_date)

    total_sent = query.filter(Message.status.in_([
        MessageStatus.SENT,
        MessageStatus.VIEWED,
        MessageStatus.REPLIED
    ])).count()

    total_viewed = query.filter(Message.status.in_([
        MessageStatus.VIEWED,
        MessageStatus.REPLIED
    ])).count()

    total_replied = query.filter(Message.status == MessageStatus.REPLIED).count()

    view_rate = round(total_viewed / total_sent * 100, 2) if total_sent > 0 else 0
    reply_rate = round(total_replied / total_sent * 100, 2) if total_sent > 0 else 0

    # 计算平均回复时间
    replied_messages = query.filter(
        and_(
            Message.status == MessageStatus.REPLIED,
            Message.sent_at.isnot(None),
            Message.replied_at.isnot(None)
        )
    ).all()

    avg_reply_time = None
    if replied_messages:
        reply_times = [
            (m.replied_at - m.sent_at).total_seconds() / 3600
            for m in replied_messages
        ]
        avg_reply_time = round(sum(reply_times) / len(reply_times), 2)

    return MessageStats(
        total_sent=total_sent,
        total_viewed=total_viewed,
        total_replied=total_replied,
        view_rate=view_rate,
        reply_rate=reply_rate,
        avg_reply_time=avg_reply_time
    )


@router.get("/stats/by-time")
def get_message_stats_by_time(db: Session = Depends(get_db)):
    """按时间段统计消息效果"""
    # 获取最近7天的数据
    seven_days_ago = datetime.now() - timedelta(days=7)

    messages = db.query(Message).filter(
        Message.sent_at >= seven_days_ago,
        Message.status.in_([MessageStatus.SENT, MessageStatus.VIEWED, MessageStatus.REPLIED])
    ).all()

    # 按小时分组统计
    hourly_stats = {}
    for hour in range(24):
        hourly_stats[hour] = {
            'sent': 0,
            'replied': 0,
            'reply_rate': 0
        }

    for message in messages:
        if message.sent_at:
            hour = message.sent_at.hour
            hourly_stats[hour]['sent'] += 1
            if message.status == MessageStatus.REPLIED:
                hourly_stats[hour]['replied'] += 1

    # 计算回复率
    for hour in hourly_stats:
        if hourly_stats[hour]['sent'] > 0:
            hourly_stats[hour]['reply_rate'] = round(
                hourly_stats[hour]['replied'] / hourly_stats[hour]['sent'] * 100, 2
            )

    return hourly_stats


@router.get("/pending-replies")
def get_pending_replies(db: Session = Depends(get_db)):
    """获取待跟进的回复"""
    # 查询已回复但未跟进的消息
    messages = db.query(Message).filter(
        Message.status == MessageStatus.REPLIED
    ).order_by(Message.replied_at.desc()).limit(50).all()

    results = []
    for message in messages:
        target = db.query(Target).filter(Target.id == message.target_id).first()
        if target:
            # 计算回复时长
            time_since_reply = None
            if message.replied_at:
                time_since_reply = (datetime.now() - message.replied_at).total_seconds() / 3600

            results.append({
                'message_id': message.id,
                'target_id': target.id,
                'target_name': target.nickname,
                'target_followers': target.followers_count,
                'reply_content': message.reply_content,
                'replied_at': message.replied_at,
                'hours_since_reply': round(time_since_reply, 1) if time_since_reply else None,
                'is_urgent': time_since_reply < 4 if time_since_reply else False
            })

    return results
