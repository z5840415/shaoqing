from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Setting
from schemas import SettingUpdate, SettingResponse
from typing import List
import json

router = APIRouter(prefix="/api/settings", tags=["系统设置"])


@router.get("/", response_model=List[SettingResponse])
def list_settings(db: Session = Depends(get_db)):
    """获取所有设置"""
    settings = db.query(Setting).all()
    return settings


@router.get("/{key}", response_model=SettingResponse)
def get_setting(key: str, db: Session = Depends(get_db)):
    """获取指定设置"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")
    return setting


@router.put("/{key}", response_model=SettingResponse)
def update_setting(key: str, setting_data: SettingUpdate, db: Session = Depends(get_db)):
    """更新设置"""
    setting = db.query(Setting).filter(Setting.key == key).first()

    if setting:
        # 更新现有设置
        setting.value = setting_data.value
        if setting_data.description:
            setting.description = setting_data.description
    else:
        # 创建新设置
        setting = Setting(
            key=key,
            value=setting_data.value,
            description=setting_data.description
        )
        db.add(setting)

    db.commit()
    db.refresh(setting)
    return setting


@router.delete("/{key}")
def delete_setting(key: str, db: Session = Depends(get_db)):
    """删除设置"""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")

    db.delete(setting)
    db.commit()
    return {"message": "删除成功"}


# ========== 特定设置的便捷接口 ==========

@router.get("/cookie/get")
def get_cookie(db: Session = Depends(get_db)):
    """获取Cookie设置"""
    setting = db.query(Setting).filter(Setting.key == "douyin_cookie").first()
    if not setting:
        return {"cookie": None, "account": None, "expire_time": None}

    try:
        data = json.loads(setting.value)
        return data
    except:
        return {"cookie": None, "account": None, "expire_time": None}


@router.post("/cookie/save")
def save_cookie(cookie_data: dict, db: Session = Depends(get_db)):
    """保存Cookie"""
    setting = db.query(Setting).filter(Setting.key == "douyin_cookie").first()

    value = json.dumps(cookie_data)

    if setting:
        setting.value = value
    else:
        setting = Setting(
            key="douyin_cookie",
            value=value,
            description="抖音登录Cookie"
        )
        db.add(setting)

    db.commit()
    return {"message": "Cookie保存成功"}


@router.post("/cookie/test")
async def test_cookie(db: Session = Depends(get_db)):
    """测试Cookie是否有效"""
    from services.douyin_sender import DouyinSender

    sender = DouyinSender()
    try:
        await sender.init()
        is_valid = await sender.test_cookie()
        await sender.close()

        return {"valid": is_valid, "message": "Cookie有效" if is_valid else "Cookie已失效"}
    except Exception as e:
        return {"valid": False, "message": f"测试失败: {str(e)}"}


@router.get("/security/get")
def get_security_config(db: Session = Depends(get_db)):
    """获取安全策略配置"""
    setting = db.query(Setting).filter(Setting.key == "security_config").first()
    if not setting:
        # 返回默认配置
        return {
            "mode": "standard",
            "min_interval": 30,
            "max_interval": 60,
            "batch_size": 30,
            "batch_rest": 600,
            "daily_limit": 100,
            "night_pause": True,
            "random_visit": True,
            "simulate_typing": True
        }

    try:
        return json.loads(setting.value)
    except:
        return {}


@router.post("/security/save")
def save_security_config(config: dict, db: Session = Depends(get_db)):
    """保存安全策略配置"""
    setting = db.query(Setting).filter(Setting.key == "security_config").first()

    value = json.dumps(config)

    if setting:
        setting.value = value
    else:
        setting = Setting(
            key="security_config",
            value=value,
            description="安全防护策略配置"
        )
        db.add(setting)

    db.commit()
    return {"message": "安全策略保存成功"}
