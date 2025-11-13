"""
话术管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models import Template
from ..schemas import (
    Template as TemplateSchema,
    TemplateCreate,
    TemplateUpdate,
    TemplateStats
)
from ..utils import TemplateEngine

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.post("/", response_model=TemplateSchema)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """创建话术模板"""
    # 检查名称是否已存在
    existing = db.query(Template).filter(Template.name == template.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="模板名称已存在")

    # 如果设置为默认，取消其他默认模板
    if template.is_default:
        db.query(Template).filter(
            Template.platform == template.platform,
            Template.is_default == True
        ).update({"is_default": False})

    db_template = Template(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/", response_model=List[TemplateSchema])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    platform: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """获取话术模板列表"""
    query = db.query(Template)

    if platform:
        query = query.filter(Template.platform == platform)
    if is_active is not None:
        query = query.filter(Template.is_active == is_active)

    templates = query.order_by(Template.reply_rate.desc()).offset(skip).limit(limit).all()
    return templates


@router.get("/{template_id}", response_model=TemplateSchema)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """获取单个话术模板"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.put("/{template_id}", response_model=TemplateSchema)
def update_template(
    template_id: int,
    template_update: TemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新话术模板"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    # 如果设置为默认，取消其他默认模板
    if template_update.is_default:
        db.query(Template).filter(
            Template.platform == template.platform,
            Template.is_default == True,
            Template.id != template_id
        ).update({"is_default": False})

    for key, value in template_update.model_dump(exclude_unset=True).items():
        setattr(template, key, value)

    db.commit()
    db.refresh(template)
    return template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """删除话术模板"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    db.delete(template)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{template_id}/preview")
def preview_template(
    template_id: int,
    target_data: dict,
    account_data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """预览话术模板渲染效果"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")

    preview = TemplateEngine.preview(template.content, target_data, account_data)
    return preview


@router.get("/stats/comparison")
def get_templates_comparison(db: Session = Depends(get_db)):
    """获取话术对比统计"""
    templates = db.query(Template).filter(Template.usage_count > 0).all()

    stats = []
    for t in templates:
        stats.append({
            "template_id": t.id,
            "template_name": t.name,
            "usage_count": t.usage_count,
            "reply_count": t.reply_count,
            "reply_rate": round(t.reply_rate * 100, 2),
            "wechat_add_count": t.wechat_add_count,
            "wechat_add_rate": round(t.wechat_add_rate * 100, 2)
        })

    return sorted(stats, key=lambda x: x['reply_rate'], reverse=True)
