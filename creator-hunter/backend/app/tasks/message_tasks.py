"""
消息发送相关任务
"""
from celery import Task
from sqlalchemy.orm import Session
import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from .celery_app import celery_app
from ..database import SessionLocal
from ..models import (
    Target,
    Template,
    Account,
    Message,
    Task as TaskModel,
    MessageStatus,
    TaskStatus,
    TargetStatus,
    AccountStatus
)
from ..automation import DouyinAutomation
from ..utils import TemplateEngine, security_manager

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """带数据库会话的Task基类"""
    _db = None

    @property
    def db(self) -> Session:
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(base=DatabaseTask, bind=True)
def send_single_message(self, message_id: int):
    """
    发送单条消息

    Args:
        message_id: 消息ID
    """
    db = self.db

    try:
        # 获取消息
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            logger.error(f"消息不存在: {message_id}")
            return {"success": False, "error": "消息不存在"}

        # 获取目标、账号
        target = db.query(Target).filter(Target.id == message.target_id).first()
        account = db.query(Account).filter(Account.id == message.account_id).first()

        if not target or not account:
            logger.error("目标或账号不存在")
            message.status = MessageStatus.FAILED
            message.error_message = "目标或账号不存在"
            db.commit()
            return {"success": False, "error": "目标或账号不存在"}

        # 检查账号是否可用
        if not account.is_active or not account.is_logged_in:
            logger.error(f"账号不可用: {account.name}")
            message.status = MessageStatus.FAILED
            message.error_message = "账号不可用"
            db.commit()
            return {"success": False, "error": "账号不可用"}

        # 检查账号是否达到限额
        if account.today_sent_count >= account.daily_limit:
            logger.error(f"账号已达每日上限: {account.name}")
            message.status = MessageStatus.FAILED
            message.error_message = "账号已达每日上限"
            db.commit()
            return {"success": False, "error": "账号已达每日上限"}

        # 更新消息状态为发送中
        message.status = MessageStatus.SENDING
        db.commit()

        # 解密Cookie
        cookies = None
        if account.cookies:
            try:
                cookies = security_manager.decrypt(account.cookies)
            except Exception as e:
                logger.error(f"解密Cookie失败: {str(e)}")

        # 执行发送
        success = asyncio.run(_send_message_async(target.profile_url, message.content, cookies))

        if success:
            # 发送成功
            message.status = MessageStatus.SENT
            message.sent_at = datetime.now()

            # 更新目标状态
            target.status = TargetStatus.SENT
            target.last_contact_time = datetime.now()
            target.contact_count += 1

            # 更新账号统计
            account.today_sent_count += 1
            account.total_sent_count += 1
            account.success_count += 1
            account.success_rate = account.success_count / account.total_sent_count
            account.last_used_at = datetime.now()

            # 更新模板统计
            if message.template_id:
                template = db.query(Template).filter(Template.id == message.template_id).first()
                if template:
                    template.usage_count += 1
                    template.last_used_at = datetime.now()

            db.commit()

            logger.info(f"消息发送成功: {message_id}")
            return {"success": True, "message_id": message_id}
        else:
            # 发送失败
            message.status = MessageStatus.FAILED
            message.error_message = "发送失败"

            # 更新账号统计
            account.failed_count += 1
            account.success_rate = account.success_count / (account.success_count + account.failed_count)

            db.commit()

            logger.error(f"消息发送失败: {message_id}")
            return {"success": False, "error": "发送失败"}

    except Exception as e:
        logger.error(f"发送消息异常: {str(e)}")
        if message:
            message.status = MessageStatus.FAILED
            message.error_message = str(e)
            db.commit()
        return {"success": False, "error": str(e)}


async def _send_message_async(profile_url: str, content: str, cookies: str = None) -> bool:
    """异步发送消息"""
    automation = DouyinAutomation(headless=True)
    try:
        await automation.initialize()
        await automation.login(cookies)
        success = await automation.send_message(profile_url, content)
        return success
    except Exception as e:
        logger.error(f"自动化发送失败: {str(e)}")
        return False
    finally:
        await automation.close()


@celery_app.task(base=DatabaseTask, bind=True)
def send_batch_messages(self, task_id: int):
    """
    批量发送消息

    Args:
        task_id: 任务ID
    """
    db = self.db

    try:
        # 获取任务
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if not task:
            logger.error(f"任务不存在: {task_id}")
            return {"success": False, "error": "任务不存在"}

        # 更新任务状态
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.current_status = "开始批量发送"
        db.commit()

        # 获取待发送的消息列表
        messages = db.query(Message).filter(
            Message.task_id == task_id,
            Message.status == MessageStatus.PENDING
        ).all()

        total = len(messages)
        task.total_count = total
        db.commit()

        # 逐条发送
        for idx, message in enumerate(messages):
            try:
                # 发送消息
                result = send_single_message.apply(args=[message.id])

                # 更新进度
                task.sent_count = idx + 1
                task.progress = int((idx + 1) / total * 100)
                task.current_status = f"正在发送第 {idx + 1}/{total} 条"

                if result.get('success'):
                    task.success_count += 1
                else:
                    task.failed_count += 1

                    # 如果设置了失败暂停，检查是否需要暂停
                    if task.pause_on_error and task.failed_count >= 3:
                        task.status = TaskStatus.PAUSED
                        task.paused_at = datetime.now()
                        task.current_status = "连续失败，已暂停"
                        db.commit()
                        logger.warning(f"任务 {task_id} 连续失败，已暂停")
                        break

                db.commit()

                # 随机间隔
                if idx < total - 1:  # 不是最后一条
                    interval = random.randint(task.interval_min, task.interval_max)
                    logger.info(f"等待 {interval} 秒后发送下一条")
                    import time
                    time.sleep(interval)

                    # 检查是否需要自动暂停休息
                    if task.auto_pause_after > 0 and (idx + 1) % task.auto_pause_after == 0:
                        logger.info(f"已发送 {task.auto_pause_after} 条，暂停 {task.auto_pause_duration} 秒")
                        time.sleep(task.auto_pause_duration)

            except Exception as e:
                logger.error(f"发送消息 {message.id} 失败: {str(e)}")
                task.failed_count += 1
                db.commit()

        # 任务完成
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        task.progress = 100
        task.current_status = f"完成！成功 {task.success_count}，失败 {task.failed_count}"
        db.commit()

        logger.info(f"批量任务 {task_id} 完成")
        return {
            "success": True,
            "total": total,
            "success_count": task.success_count,
            "failed_count": task.failed_count
        }

    except Exception as e:
        logger.error(f"批量发送异常: {str(e)}")
        if task:
            task.status = TaskStatus.FAILED
            task.current_status = f"失败：{str(e)}"
            db.commit()
        return {"success": False, "error": str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def check_account_health(self, account_id: int):
    """检查账号健康度"""
    db = self.db

    try:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            return {"success": False, "error": "账号不存在"}

        # 计算健康度评分
        health_score = 100

        # 成功率影响（40%）
        if account.success_rate < 0.95:
            health_score -= (0.95 - account.success_rate) * 100 * 0.4
        if account.success_rate < 0.80:
            health_score -= 20

        # 使用量影响（20%）
        if account.today_sent_count >= account.daily_limit:
            health_score -= 20

        # 登录状态影响（30%）
        if not account.is_logged_in:
            health_score -= 30

        # 错误次数影响（10%）
        if account.failed_count > 10:
            health_score -= 10

        health_score = max(0, min(100, int(health_score)))

        # 更新健康度
        account.health_score = health_score

        # 更新状态
        if health_score >= 90:
            account.status = AccountStatus.ACTIVE
        elif health_score >= 70:
            account.status = AccountStatus.WARNING
        else:
            account.status = AccountStatus.ABNORMAL

        account.last_check_time = datetime.now()
        db.commit()

        logger.info(f"账号 {account.name} 健康度: {health_score}")
        return {"success": True, "health_score": health_score}

    except Exception as e:
        logger.error(f"检查账号健康度失败: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def reset_daily_counts(self):
    """重置所有账号的每日计数"""
    db = self.db
    try:
        accounts = db.query(Account).all()
        for account in accounts:
            account.today_sent_count = 0
        db.commit()
        logger.info("已重置所有账号的每日计数")
        return {"success": True, "count": len(accounts)}
    except Exception as e:
        logger.error(f"重置每日计数失败: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def check_all_accounts_health(self):
    """检查所有账号健康度"""
    db = self.db
    try:
        accounts = db.query(Account).filter(Account.is_active == True).all()
        for account in accounts:
            check_account_health.delay(account.id)
        logger.info(f"已提交 {len(accounts)} 个账号的健康度检查任务")
        return {"success": True, "count": len(accounts)}
    except Exception as e:
        logger.error(f"检查所有账号健康度失败: {str(e)}")
        return {"success": False, "error": str(e)}


@celery_app.task(base=DatabaseTask, bind=True)
def generate_followup_reminders(self):
    """生成跟进提醒"""
    db = self.db
    try:
        now = datetime.now()
        reminders = []

        # 1. 已回复但超过4小时未跟进
        replied_targets = db.query(Target).filter(
            Target.status == TargetStatus.REPLIED
        ).all()

        for target in replied_targets:
            last_message = db.query(Message).filter(
                Message.target_id == target.id,
                Message.status == MessageStatus.REPLIED
            ).order_by(Message.replied_at.desc()).first()

            if last_message and last_message.replied_at:
                hours_since_reply = (now - last_message.replied_at).total_seconds() / 3600
                if hours_since_reply >= 4:
                    reminders.append({
                        "type": "reply_pending",
                        "target_id": target.id,
                        "target_name": target.nickname,
                        "message": f"创作者 {target.nickname} 已回复 {hours_since_reply:.1f} 小时，请及时跟进"
                    })

        # 2. 未回复超过48小时
        sent_targets = db.query(Target).filter(
            Target.status == TargetStatus.SENT,
            Target.last_contact_time.isnot(None)
        ).all()

        for target in sent_targets:
            hours_since_contact = (now - target.last_contact_time).total_seconds() / 3600
            if hours_since_contact >= 48:
                reminders.append({
                    "type": "no_reply",
                    "target_id": target.id,
                    "target_name": target.nickname,
                    "message": f"创作者 {target.nickname} 已发送 {hours_since_contact:.1f} 小时未回复，考虑跟进"
                })

        logger.info(f"生成了 {len(reminders)} 条跟进提醒")
        # TODO: 发送提醒通知（邮件、企业微信等）

        return {"success": True, "reminders": reminders}

    except Exception as e:
        logger.error(f"生成跟进提醒失败: {str(e)}")
        return {"success": False, "error": str(e)}
