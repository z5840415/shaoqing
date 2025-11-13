"""
目标管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import pandas as pd
import json
from io import BytesIO

from ..database import get_db
from ..models import Target, TargetStatus
from ..schemas import (
    Target as TargetSchema,
    TargetCreate,
    TargetUpdate,
    TargetFilter,
    TargetImport
)

router = APIRouter(prefix="/api/targets", tags=["targets"])


@router.post("/", response_model=TargetSchema)
def create_target(target: TargetCreate, db: Session = Depends(get_db)):
    """创建目标创作者"""
    # 检查是否已存在
    existing = db.query(Target).filter(Target.platform_id == target.platform_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该创作者已存在")

    db_target = Target(**target.model_dump())
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target


@router.get("/", response_model=List[TargetSchema])
def list_targets(
    skip: int = 0,
    limit: int = 100,
    status: Optional[TargetStatus] = None,
    platform: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取目标创作者列表"""
    query = db.query(Target)

    # 筛选条件
    if status:
        query = query.filter(Target.status == status)
    if platform:
        query = query.filter(Target.platform == platform)
    if search:
        query = query.filter(
            or_(
                Target.nickname.contains(search),
                Target.platform_id.contains(search),
                Target.notes.contains(search)
            )
        )

    targets = query.order_by(Target.priority.desc(), Target.created_at.desc()).offset(skip).limit(limit).all()
    return targets


@router.get("/{target_id}", response_model=TargetSchema)
def get_target(target_id: int, db: Session = Depends(get_db)):
    """获取单个目标创作者"""
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="目标不存在")
    return target


@router.put("/{target_id}", response_model=TargetSchema)
def update_target(target_id: int, target_update: TargetUpdate, db: Session = Depends(get_db)):
    """更新目标创作者"""
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="目标不存在")

    # 更新字段
    for key, value in target_update.model_dump(exclude_unset=True).items():
        setattr(target, key, value)

    db.commit()
    db.refresh(target)
    return target


@router.delete("/{target_id}")
def delete_target(target_id: int, db: Session = Depends(get_db)):
    """删除目标创作者"""
    target = db.query(Target).filter(Target.id == target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="目标不存在")

    db.delete(target)
    db.commit()
    return {"message": "删除成功"}


@router.post("/batch")
def batch_import_targets(targets_data: TargetImport, db: Session = Depends(get_db)):
    """批量导入目标创作者"""
    success_count = 0
    failed_count = 0
    skipped_count = 0
    errors = []

    for idx, target_data in enumerate(targets_data.targets):
        try:
            # 检查是否已存在
            existing = db.query(Target).filter(Target.platform_id == target_data.platform_id).first()
            if existing:
                skipped_count += 1
                continue

            db_target = Target(**target_data.model_dump())
            db.add(db_target)
            success_count += 1
        except Exception as e:
            failed_count += 1
            errors.append(f"第{idx + 1}行：{str(e)}")

    db.commit()

    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "skipped_count": skipped_count,
        "errors": errors
    }


@router.post("/import-excel")
async def import_from_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """从Excel文件导入目标创作者"""
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="仅支持Excel或CSV文件")

    try:
        # 读取文件
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(BytesIO(contents))
        else:
            df = pd.read_excel(BytesIO(contents))

        # 验证必填列
        required_columns = ['抖音昵称', '抖音ID', '抖音主页链接']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(status_code=400, detail=f"缺少必填列：{', '.join(missing_columns)}")

        success_count = 0
        failed_count = 0
        skipped_count = 0
        errors = []

        # 逐行处理
        for idx, row in df.iterrows():
            try:
                # 检查必填项
                if pd.isna(row['抖音ID']) or pd.isna(row['抖音昵称']):
                    failed_count += 1
                    errors.append(f"第{idx + 2}行：缺少必填项")
                    continue

                # 检查是否已存在
                existing = db.query(Target).filter(Target.platform_id == str(row['抖音ID'])).first()
                if existing:
                    skipped_count += 1
                    continue

                # 创建目标
                target = Target(
                    nickname=str(row['抖音昵称']),
                    platform_id=str(row['抖音ID']),
                    profile_url=str(row['抖音主页链接']) if not pd.isna(row['抖音主页链接']) else None,
                    followers_count=int(row['粉丝数']) if '粉丝数' in df.columns and not pd.isna(row['粉丝数']) else 0,
                    avg_views=int(row['平均播放量']) if '平均播放量' in df.columns and not pd.isna(row['平均播放量']) else 0,
                    tags=str(row['内容标签']) if '内容标签' in df.columns and not pd.isna(row['内容标签']) else None,
                    notes=str(row['备注']) if '备注' in df.columns and not pd.isna(row['备注']) else None
                )
                db.add(target)
                success_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(f"第{idx + 2}行：{str(e)}")

        db.commit()

        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "skipped_count": skipped_count,
            "errors": errors[:10]  # 只返回前10个错误
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入失败：{str(e)}")


@router.get("/stats/overview")
def get_targets_stats(db: Session = Depends(get_db)):
    """获取目标统计概览"""
    total = db.query(Target).count()
    pending = db.query(Target).filter(Target.status == TargetStatus.PENDING).count()
    sent = db.query(Target).filter(Target.status == TargetStatus.SENT).count()
    replied = db.query(Target).filter(Target.status == TargetStatus.REPLIED).count()
    added_wechat = db.query(Target).filter(Target.status == TargetStatus.ADDED_WECHAT).count()
    signed = db.query(Target).filter(Target.status == TargetStatus.SIGNED).count()

    return {
        "total": total,
        "pending": pending,
        "sent": sent,
        "replied": replied,
        "added_wechat": added_wechat,
        "signed": signed,
        "reply_rate": round(replied / sent * 100, 2) if sent > 0 else 0,
        "wechat_rate": round(added_wechat / replied * 100, 2) if replied > 0 else 0,
        "signed_rate": round(signed / added_wechat * 100, 2) if added_wechat > 0 else 0
    }
