"""
数据分析 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import Optional

from ..database import get_db
from ..models import (
    Target,
    Message,
    Template,
    Account,
    TargetStatus,
    MessageStatus
)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """获取仪表板统计数据"""
    # 今日数据
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    today_sent = db.query(Message).filter(
        Message.sent_at >= today_start,
        Message.status.in_([MessageStatus.SENT, MessageStatus.VIEWED, MessageStatus.REPLIED])
    ).count()

    today_replied = db.query(Message).filter(
        Message.replied_at >= today_start,
        Message.status == MessageStatus.REPLIED
    ).count()

    # 本周数据
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    week_sent = db.query(Message).filter(
        Message.sent_at >= week_start
    ).count()

    week_signed = db.query(Target).filter(
        Target.signed_time >= week_start
    ).count()

    # 本月数据
    month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month_sent = db.query(Message).filter(
        Message.sent_at >= month_start
    ).count()

    month_replied = db.query(Message).filter(
        Message.replied_at >= month_start,
        Message.status == MessageStatus.REPLIED
    ).count()

    month_signed = db.query(Target).filter(
        Target.signed_time >= month_start
    ).count()

    # 总体数据
    total_targets = db.query(Target).count()
    total_messages = db.query(Message).count()
    total_signed = db.query(Target).filter(Target.status == TargetStatus.SIGNED).count()

    return {
        "today": {
            "sent": today_sent,
            "replied": today_replied,
            "reply_rate": round(today_replied / today_sent * 100, 2) if today_sent > 0 else 0
        },
        "this_week": {
            "sent": week_sent,
            "signed": week_signed
        },
        "this_month": {
            "sent": month_sent,
            "replied": month_replied,
            "signed": month_signed,
            "reply_rate": round(month_replied / month_sent * 100, 2) if month_sent > 0 else 0,
            "conversion_rate": round(month_signed / month_sent * 100, 2) if month_sent > 0 else 0
        },
        "total": {
            "targets": total_targets,
            "messages": total_messages,
            "signed": total_signed
        }
    }


@router.get("/conversion-funnel")
def get_conversion_funnel(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """获取转化漏斗数据"""
    query = db.query(Message)

    if start_date:
        query = query.filter(Message.created_at >= start_date)
    if end_date:
        query = query.filter(Message.created_at <= end_date)

    # 触达（已发送）
    sent_count = query.filter(Message.status.in_([
        MessageStatus.SENT,
        MessageStatus.VIEWED,
        MessageStatus.REPLIED
    ])).count()

    # 已查看
    viewed_count = query.filter(Message.status.in_([
        MessageStatus.VIEWED,
        MessageStatus.REPLIED
    ])).count()

    # 已回复
    replied_count = query.filter(Message.status == MessageStatus.REPLIED).count()

    # 已添加微信
    added_wechat_count = db.query(Target).filter(
        Target.wechat_added_time.isnot(None)
    ).count()

    # 已签约
    signed_count = db.query(Target).filter(
        Target.status == TargetStatus.SIGNED
    ).count()

    funnel = {
        "sent": {
            "count": sent_count,
            "rate": 100.0
        },
        "viewed": {
            "count": viewed_count,
            "rate": round(viewed_count / sent_count * 100, 2) if sent_count > 0 else 0
        },
        "replied": {
            "count": replied_count,
            "rate": round(replied_count / sent_count * 100, 2) if sent_count > 0 else 0
        },
        "added_wechat": {
            "count": added_wechat_count,
            "rate": round(added_wechat_count / replied_count * 100, 2) if replied_count > 0 else 0
        },
        "signed": {
            "count": signed_count,
            "rate": round(signed_count / added_wechat_count * 100, 2) if added_wechat_count > 0 else 0
        },
        "overall_conversion_rate": round(signed_count / sent_count * 100, 2) if sent_count > 0 else 0
    }

    return funnel


@router.get("/best-time-analysis")
def get_best_time_analysis(db: Session = Depends(get_db)):
    """分析最佳发送时间"""
    # 获取最近30天的数据
    thirty_days_ago = datetime.now() - timedelta(days=30)

    messages = db.query(Message).filter(
        Message.sent_at >= thirty_days_ago,
        Message.status.in_([MessageStatus.SENT, MessageStatus.VIEWED, MessageStatus.REPLIED])
    ).all()

    # 按时间段分组
    time_slots = {
        "09-12": {"sent": 0, "replied": 0, "reply_rate": 0},
        "12-14": {"sent": 0, "replied": 0, "reply_rate": 0},
        "14-17": {"sent": 0, "replied": 0, "reply_rate": 0},
        "17-19": {"sent": 0, "replied": 0, "reply_rate": 0},
        "19-22": {"sent": 0, "replied": 0, "reply_rate": 0},
        "22-24": {"sent": 0, "replied": 0, "reply_rate": 0}
    }

    for message in messages:
        if message.sent_at:
            hour = message.sent_at.hour
            slot = None

            if 9 <= hour < 12:
                slot = "09-12"
            elif 12 <= hour < 14:
                slot = "12-14"
            elif 14 <= hour < 17:
                slot = "14-17"
            elif 17 <= hour < 19:
                slot = "17-19"
            elif 19 <= hour < 22:
                slot = "19-22"
            elif 22 <= hour < 24:
                slot = "22-24"

            if slot:
                time_slots[slot]["sent"] += 1
                if message.status == MessageStatus.REPLIED:
                    time_slots[slot]["replied"] += 1

    # 计算回复率并找出最佳时间段
    best_slots = []
    for slot, data in time_slots.items():
        if data["sent"] > 0:
            data["reply_rate"] = round(data["replied"] / data["sent"] * 100, 2)
            best_slots.append({"slot": slot, "reply_rate": data["reply_rate"]})

    best_slots.sort(key=lambda x: x["reply_rate"], reverse=True)

    return {
        "time_slots": time_slots,
        "best_time_slots": best_slots[:3],
        "recommendation": f"建议在 {best_slots[0]['slot']} 时间段发送，回复率最高（{best_slots[0]['reply_rate']}%）" if best_slots else "数据不足"
    }


@router.get("/template-performance")
def get_template_performance(db: Session = Depends(get_db)):
    """获取话术性能对比"""
    templates = db.query(Template).filter(Template.usage_count > 0).all()

    performance = []
    for template in templates:
        # 查询使用该模板的消息
        messages = db.query(Message).filter(Message.template_id == template.id).all()

        sent_count = len([m for m in messages if m.status in [
            MessageStatus.SENT,
            MessageStatus.VIEWED,
            MessageStatus.REPLIED
        ]])

        replied_count = len([m for m in messages if m.status == MessageStatus.REPLIED])

        # 计算平均回复时间
        reply_times = [
            (m.replied_at - m.sent_at).total_seconds() / 3600
            for m in messages
            if m.replied_at and m.sent_at
        ]
        avg_reply_time = round(sum(reply_times) / len(reply_times), 2) if reply_times else None

        performance.append({
            "template_id": template.id,
            "template_name": template.name,
            "usage_count": sent_count,
            "reply_count": replied_count,
            "reply_rate": round(replied_count / sent_count * 100, 2) if sent_count > 0 else 0,
            "avg_reply_time_hours": avg_reply_time,
            "last_used": template.last_used_at
        })

    # 按回复率排序
    performance.sort(key=lambda x: x["reply_rate"], reverse=True)

    return performance


@router.get("/follower-analysis")
def get_follower_analysis(db: Session = Depends(get_db)):
    """按粉丝量分析转化效果"""
    # 定义粉丝量区间
    ranges = [
        {"name": "<5000", "min": 0, "max": 5000},
        {"name": "5000-10000", "min": 5000, "max": 10000},
        {"name": "10000-50000", "min": 10000, "max": 50000},
        {"name": "50000-100000", "min": 50000, "max": 100000},
        {"name": ">100000", "min": 100000, "max": 999999999}
    ]

    analysis = []
    for r in ranges:
        targets = db.query(Target).filter(
            and_(
                Target.followers_count >= r["min"],
                Target.followers_count < r["max"]
            )
        ).all()

        total = len(targets)
        replied = len([t for t in targets if t.status in [
            TargetStatus.REPLIED,
            TargetStatus.ADDED_WECHAT,
            TargetStatus.SIGNED
        ]])
        signed = len([t for t in targets if t.status == TargetStatus.SIGNED])

        analysis.append({
            "range": r["name"],
            "total_contacted": total,
            "replied_count": replied,
            "reply_rate": round(replied / total * 100, 2) if total > 0 else 0,
            "signed_count": signed,
            "signed_rate": round(signed / total * 100, 2) if total > 0 else 0
        })

    return analysis
