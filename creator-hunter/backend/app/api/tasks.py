"""
任务管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from ..database import get_db
from ..models import Task, TaskStatus, Message, MessageStatus, Target, Template, Account
from ..schemas import (
    Task as TaskSchema,
    TaskCreate,
    TaskUpdate,
    TaskProgress
)
from ..tasks import send_single_message, send_batch_messages
from ..utils import TemplateEngine

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/", response_model=TaskSchema)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """创建发送任务"""
    # 解析目标ID列表
    try:
        target_ids = json.loads(task.target_ids) if isinstance(task.target_ids, str) else task.target_ids
    except:
        raise HTTPException(status_code=400, detail="目标ID列表格式错误")

    # 验证目标是否存在
    targets = db.query(Target).filter(Target.id.in_(target_ids)).all()
    if len(targets) != len(target_ids):
        raise HTTPException(status_code=400, detail="部分目标不存在")

    # 创建任务
    db_task = Task(**task.model_dump())
    db_task.total_count = len(target_ids)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    # 获取模板
    template = None
    if task.template_id:
        template = db.query(Template).filter(Template.id == task.template_id).first()

    # 获取账号（如果指定了账号列表）
    account_ids = None
    if task.account_ids:
        try:
            account_ids = json.loads(task.account_ids) if isinstance(task.account_ids, str) else task.account_ids
        except:
            account_ids = None

    # 如果没有指定账号，获取所有可用账号
    if not account_ids:
        accounts = db.query(Account).filter(
            Account.is_active == True,
            Account.is_logged_in == True
        ).all()
        account_ids = [acc.id for acc in accounts]

    if not account_ids:
        raise HTTPException(status_code=400, detail="没有可用的账号")

    # 为每个目标创建消息记录
    account_index = 0
    for target_id in target_ids:
        # 轮换账号
        if task.account_rotation and len(account_ids) > 1:
            account_id = account_ids[account_index % len(account_ids)]
            account_index += 1
        else:
            account_id = account_ids[0]

        # 生成消息内容
        target = db.query(Target).filter(Target.id == target_id).first()
        account = db.query(Account).filter(Account.id == account_id).first()

        content = template.content if template else ""
        if template:
            # 渲染模板
            variables = TemplateEngine.build_variables(
                target_data={
                    'nickname': target.nickname,
                    'followers_count': target.followers_count,
                    'tags': target.tags
                },
                account_data={
                    'wechat_id': account.wechat_id,
                    'operator_name': account.operator_name
                }
            )
            content = TemplateEngine.render(template.content, variables)

        # 创建消息
        message = Message(
            target_id=target_id,
            template_id=task.template_id,
            account_id=account_id,
            task_id=db_task.id,
            content=content,
            original_template=template.content if template else None,
            status=MessageStatus.PENDING
        )
        db.add(message)

    db.commit()

    return db_task


@router.get("/", response_model=List[TaskSchema])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)

    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=TaskSchema)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """获取单个任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("/{task_id}/start")
def start_task(task_id: int, db: Session = Depends(get_db)):
    """启动任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.PENDING:
        raise HTTPException(status_code=400, detail="任务状态不允许启动")

    # 提交到Celery
    send_batch_messages.delay(task_id)

    return {"message": "任务已启动"}


@router.post("/{task_id}/pause")
def pause_task(task_id: int, db: Session = Depends(get_db)):
    """暂停任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.RUNNING:
        raise HTTPException(status_code=400, detail="任务未在运行")

    task.status = TaskStatus.PAUSED
    task.paused_at = datetime.now()
    db.commit()

    return {"message": "任务已暂停"}


@router.post("/{task_id}/resume")
def resume_task(task_id: int, db: Session = Depends(get_db)):
    """恢复任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status != TaskStatus.PAUSED:
        raise HTTPException(status_code=400, detail="任务未暂停")

    # 重新提交到Celery
    send_batch_messages.delay(task_id)

    return {"message": "任务已恢复"}


@router.post("/{task_id}/cancel")
def cancel_task(task_id: int, db: Session = Depends(get_db)):
    """取消任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = TaskStatus.CANCELLED
    db.commit()

    return {"message": "任务已取消"}


@router.get("/{task_id}/progress", response_model=TaskProgress)
def get_task_progress(task_id: int, db: Session = Depends(get_db)):
    """获取任务进度"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return TaskProgress(
        task_id=task.id,
        task_name=task.name,
        status=task.status,
        progress=task.progress,
        sent_count=task.sent_count,
        success_count=task.success_count,
        failed_count=task.failed_count,
        total_count=task.total_count,
        current_status=task.current_status,
        estimated_completion_time=task.estimated_completion_time
    )


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """删除任务"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 只能删除已完成、已取消或失败的任务
    if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
        raise HTTPException(status_code=400, detail="无法删除进行中的任务")

    db.delete(task)
    db.commit()

    return {"message": "删除成功"}


from datetime import datetime
