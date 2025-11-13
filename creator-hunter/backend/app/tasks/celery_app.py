"""
Celery应用配置
"""
from celery import Celery
from celery.schedules import crontab
from ..config import settings

# 创建Celery应用
celery_app = Celery(
    "creator_hunter",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.message_tasks"
    ]
)

# 配置
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30分钟超时
    task_soft_time_limit=25 * 60,  # 25分钟软超时
)

# 定时任务配置
celery_app.conf.beat_schedule = {
    # 每天凌晨0点重置账号每日计数
    'reset-daily-counts': {
        'task': 'app.tasks.message_tasks.reset_daily_counts',
        'schedule': crontab(hour=0, minute=0),
    },
    # 每小时检查账号健康度
    'check-accounts-health': {
        'task': 'app.tasks.message_tasks.check_all_accounts_health',
        'schedule': crontab(minute=0),  # 每小时整点
    },
    # 每天早上9点和晚上8点生成跟进提醒
    'generate-followup-reminders-morning': {
        'task': 'app.tasks.message_tasks.generate_followup_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    'generate-followup-reminders-evening': {
        'task': 'app.tasks.message_tasks.generate_followup_reminders',
        'schedule': crontab(hour=20, minute=0),
    },
}
