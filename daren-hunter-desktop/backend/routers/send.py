from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Target, Template, SendLog, Setting
from schemas import SendConfig, SendProgress, SendResult, SendLogResponse
from datetime import datetime, timedelta
import json
from sqlalchemy import func, and_

router = APIRouter(prefix="/api/send", tags=["发送任务"])

# 全局变量存储当前发送状态
current_send_task = {
    "running": False,
    "progress": None,
    "should_stop": False,
    "should_pause": False
}


@router.post("/start")
async def start_send(
    config: SendConfig,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """开始发送任务"""
    if current_send_task["running"]:
        raise HTTPException(status_code=400, detail="已有发送任务在运行中")

    # 验证目标和模板
    targets = db.query(Target).filter(Target.id.in_(config.target_ids)).all()
    if not targets:
        raise HTTPException(status_code=400, detail="没有找到目标达人")

    template = db.query(Template).filter(Template.id == config.template_id).first()
    if not template:
        raise HTTPException(status_code=400, detail="话术模板不存在")

    # 检查每日限制
    today = datetime.now().date()
    today_sent = db.query(func.count(SendLog.id)).filter(
        and_(
            func.date(SendLog.send_time) == today,
            SendLog.status == "success"
        )
    ).scalar()

    if today_sent >= config.daily_limit:
        raise HTTPException(status_code=400, detail=f"今日已达到发送上限 ({config.daily_limit}条)")

    # 初始化进度
    current_send_task["running"] = True
    current_send_task["should_stop"] = False
    current_send_task["should_pause"] = False
    current_send_task["progress"] = {
        "total": len(targets),
        "sent": 0,
        "success": 0,
        "failed": 0,
        "remaining": len(targets),
        "progress": 0.0,
        "current_target": None,
        "estimated_completion": None
    }

    # 在后台执行发送任务
    background_tasks.add_task(execute_send_task, config, targets, template, db)

    return {"message": "发送任务已启动", "task_id": datetime.now().timestamp()}


async def execute_send_task(config: SendConfig, targets: List[Target], template: Template, db: Session):
    """执行发送任务的后台函数"""
    import asyncio
    import random
    from services.douyin_sender import DouyinSender

    sender = DouyinSender()
    success_count = 0
    failed_count = 0
    failed_reasons = {}

    try:
        # 初始化Playwright（加载Cookie等）
        await sender.init()

        for idx, target in enumerate(targets):
            # 检查是否应该停止
            if current_send_task["should_stop"]:
                break

            # 检查是否应该暂停
            while current_send_task["should_pause"]:
                await asyncio.sleep(1)

            # 更新进度
            current_send_task["progress"]["current_target"] = target.nickname
            current_send_task["progress"]["sent"] = idx + 1

            # 替换话术变量
            message = template.content
            message = message.replace("{昵称}", target.nickname)
            message = message.replace("{粉丝数}", str(target.fans_count))
            # 可以添加更多变量替换

            # 发送私信
            try:
                result = await sender.send_message(target.homepage_url, message)

                if result["success"]:
                    success_count += 1
                    # 记录成功日志
                    log = SendLog(
                        target_id=target.id,
                        target_nickname=target.nickname,
                        template_id=template.id,
                        template_name=template.name,
                        message_content=message,
                        status="success",
                        send_time=datetime.now()
                    )
                    db.add(log)

                    # 更新达人状态
                    target.status = "sent"
                else:
                    failed_count += 1
                    error = result.get("error", "未知错误")
                    failed_reasons[error] = failed_reasons.get(error, 0) + 1

                    # 记录失败日志
                    log = SendLog(
                        target_id=target.id,
                        target_nickname=target.nickname,
                        template_id=template.id,
                        template_name=template.name,
                        message_content=message,
                        status="failed",
                        error_message=error,
                        send_time=datetime.now()
                    )
                    db.add(log)

            except Exception as e:
                failed_count += 1
                error = str(e)
                failed_reasons[error] = failed_reasons.get(error, 0) + 1

                # 记录异常日志
                log = SendLog(
                    target_id=target.id,
                    target_nickname=target.nickname,
                    template_id=template.id,
                    template_name=template.name,
                    message_content=message,
                    status="failed",
                    error_message=error,
                    send_time=datetime.now()
                )
                db.add(log)

            # 更新模板使用次数
            template.usage_count += 1

            # 提交数据库
            db.commit()

            # 更新进度
            current_send_task["progress"]["success"] = success_count
            current_send_task["progress"]["failed"] = failed_count
            current_send_task["progress"]["remaining"] = len(targets) - idx - 1
            current_send_task["progress"]["progress"] = (idx + 1) / len(targets) * 100

            # 随机间隔
            if idx < len(targets) - 1:  # 不是最后一个
                interval = random.randint(config.min_interval, config.max_interval)
                await asyncio.sleep(interval)

                # 批次休息
                if (idx + 1) % config.batch_size == 0:
                    await asyncio.sleep(config.batch_rest)

    finally:
        # 清理
        await sender.close()
        current_send_task["running"] = False
        current_send_task["progress"] = None


@router.get("/progress", response_model=SendProgress)
def get_progress():
    """获取发送进度"""
    if not current_send_task["running"]:
        raise HTTPException(status_code=404, detail="没有正在运行的任务")

    return current_send_task["progress"]


@router.post("/pause")
def pause_send():
    """暂停发送"""
    if not current_send_task["running"]:
        raise HTTPException(status_code=404, detail="没有正在运行的任务")

    current_send_task["should_pause"] = True
    return {"message": "任务已暂停"}


@router.post("/resume")
def resume_send():
    """恢复发送"""
    if not current_send_task["running"]:
        raise HTTPException(status_code=404, detail="没有正在运行的任务")

    current_send_task["should_pause"] = False
    return {"message": "任务已恢复"}


@router.post("/stop")
def stop_send():
    """停止发送"""
    if not current_send_task["running"]:
        raise HTTPException(status_code=404, detail="没有正在运行的任务")

    current_send_task["should_stop"] = True
    return {"message": "任务正在停止..."}


@router.get("/logs", response_model=List[SendLogResponse])
def get_send_logs(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """获取发送记录"""
    query = db.query(SendLog)

    if status:
        query = query.filter(SendLog.status == status)

    logs = query.order_by(SendLog.send_time.desc()).offset(skip).limit(limit).all()
    return logs


@router.get("/status")
def get_send_status():
    """获取当前发送状态"""
    return {
        "running": current_send_task["running"],
        "has_progress": current_send_task["progress"] is not None
    }
