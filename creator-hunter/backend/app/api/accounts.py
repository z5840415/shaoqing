"""
账号管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..models import Account, AccountStatus
from ..schemas import (
    Account as AccountSchema,
    AccountCreate,
    AccountUpdate,
    AccountHealth
)
from ..utils import security_manager

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.post("/", response_model=AccountSchema)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    """创建账号"""
    # 加密Cookie
    encrypted_cookies = None
    if account.cookies:
        encrypted_cookies = security_manager.encrypt(account.cookies)

    account_data = account.model_dump()
    account_data['cookies'] = encrypted_cookies

    db_account = Account(**account_data)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    # 返回时不包含Cookie
    return db_account


@router.get("/", response_model=List[AccountSchema])
def list_accounts(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取账号列表"""
    query = db.query(Account)

    if platform:
        query = query.filter(Account.platform == platform)
    if is_active is not None:
        query = query.filter(Account.is_active == is_active)

    accounts = query.order_by(Account.health_score.desc()).offset(skip).limit(limit).all()
    return accounts


@router.get("/{account_id}", response_model=AccountSchema)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """获取单个账号"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    return account


@router.put("/{account_id}", response_model=AccountSchema)
def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db)
):
    """更新账号"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    update_data = account_update.model_dump(exclude_unset=True)

    # 如果更新Cookie，需要加密
    if 'cookies' in update_data and update_data['cookies']:
        update_data['cookies'] = security_manager.encrypt(update_data['cookies'])

    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """删除账号"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    db.delete(account)
    db.commit()
    return {"message": "删除成功"}


@router.get("/{account_id}/cookies")
def get_account_cookies(account_id: int, db: Session = Depends(get_db)):
    """获取账号Cookie（解密）"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    cookies = None
    if account.cookies:
        try:
            cookies = security_manager.decrypt(account.cookies)
        except Exception:
            cookies = None

    return {"cookies": cookies}


@router.get("/{account_id}/health", response_model=AccountHealth)
def get_account_health(account_id: int, db: Session = Depends(get_db)):
    """获取账号健康度"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    # 生成建议
    recommendations = []
    if account.health_score < 70:
        recommendations.append("账号健康度较低，建议暂停使用并检查")
    if account.success_rate < 0.9:
        recommendations.append("发送成功率偏低，可能被限流")
    if account.today_sent_count >= account.daily_limit * 0.9:
        recommendations.append("今日发送量接近上限，建议降低频率")
    if not account.is_logged_in:
        recommendations.append("账号未登录，请重新登录")

    return AccountHealth(
        account_id=account.id,
        account_name=account.name,
        health_score=account.health_score,
        status=account.status,
        success_rate=account.success_rate,
        today_sent=account.today_sent_count,
        daily_limit=account.daily_limit,
        recommendations=recommendations
    )


@router.post("/{account_id}/reset-daily-count")
def reset_daily_count(account_id: int, db: Session = Depends(get_db)):
    """重置今日发送计数（每天自动调用）"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")

    account.today_sent_count = 0
    db.commit()

    return {"message": "重置成功"}


@router.get("/stats/health-overview")
def get_health_overview(db: Session = Depends(get_db)):
    """获取账号健康度概览"""
    accounts = db.query(Account).filter(Account.is_active == True).all()

    total = len(accounts)
    healthy = len([a for a in accounts if a.health_score >= 90])
    warning = len([a for a in accounts if 70 <= a.health_score < 90])
    abnormal = len([a for a in accounts if a.health_score < 70])

    return {
        "total": total,
        "healthy": healthy,
        "warning": warning,
        "abnormal": abnormal,
        "avg_health_score": round(sum([a.health_score for a in accounts]) / total, 2) if total > 0 else 0
    }
