from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db, Template
from schemas import TemplateCreate, TemplateUpdate, TemplateResponse

router = APIRouter(prefix="/api/templates", tags=["话术管理"])


@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """创建新话术"""
    # 如果设置为默认，取消其他默认话术
    if template.is_default:
        db.query(Template).update({"is_default": False})

    db_template = Template(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.get("/", response_model=List[TemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    """获取话术列表"""
    templates = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """获取话术详情"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="话术不存在")
    return template


@router.get("/default/get", response_model=TemplateResponse)
def get_default_template(db: Session = Depends(get_db)):
    """获取默认话术"""
    template = db.query(Template).filter(Template.is_default == True).first()
    if not template:
        # 如果没有默认话术，返回第一个
        template = db.query(Template).first()
    if not template:
        raise HTTPException(status_code=404, detail="没有可用的话术")
    return template


@router.put("/{template_id}", response_model=TemplateResponse)
def update_template(template_id: int, template: TemplateUpdate, db: Session = Depends(get_db)):
    """更新话术"""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="话术不存在")

    # 如果设置为默认，取消其他默认话术
    if template.is_default:
        db.query(Template).filter(Template.id != template_id).update({"is_default": False})

    for key, value in template.dict(exclude_unset=True).items():
        setattr(db_template, key, value)

    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """删除话术"""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="话术不存在")

    db.delete(db_template)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{template_id}/set-default", response_model=TemplateResponse)
def set_default_template(template_id: int, db: Session = Depends(get_db)):
    """设置为默认话术"""
    db_template = db.query(Template).filter(Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="话术不存在")

    # 取消其他默认话术
    db.query(Template).update({"is_default": False})

    # 设置当前为默认
    db_template.is_default = True
    db.commit()
    db.refresh(db_template)
    return db_template


@router.post("/{template_id}/preview")
def preview_template(template_id: int, variables: dict, db: Session = Depends(get_db)):
    """预览话术效果（替换变量）"""
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="话术不存在")

    content = template.content
    # 替换变量
    for key, value in variables.items():
        content = content.replace(f"{{{key}}}", str(value))

    return {"content": content, "char_count": len(content)}
