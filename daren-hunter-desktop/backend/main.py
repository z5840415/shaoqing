from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from database import init_db, get_db, Template, Setting
from routers import targets, templates, send, statistics, settings
from sqlalchemy.orm import Session
import json

# 创建FastAPI应用
app = FastAPI(
    title="达人猎手 API",
    description="AIGC达人自动化建联工具后端API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(targets.router)
app.include_router(templates.router)
app.include_router(send.router)
app.include_router(statistics.router)
app.include_router(settings.router)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    # 初始化数据库
    init_db()
    print("数据库初始化完成")

    # 创建默认数据
    create_default_data()
    print("默认数据创建完成")

    # 安装Playwright浏览器
    try:
        import subprocess
        subprocess.run(["playwright", "install", "chromium"], check=False, capture_output=True)
        print("Playwright浏览器安装完成")
    except:
        print("Playwright浏览器安装失败（可能已安装）")


def create_default_data():
    """创建默认数据"""
    from database import SessionLocal

    db = SessionLocal()
    try:
        # 检查是否有话术模板
        template_count = db.query(Template).count()
        if template_count == 0:
            # 创建默认话术
            default_templates = [
                Template(
                    name="首次触达-标准版",
                    content="您好，我是网易旗下永劫无间生态内容的运营，我们每个月针对AI作者有一个扶持计划，每月发布4-10条永劫无间相关内容最多可获得1.5万激励，爆款视频还有额外激励，感兴趣请加我v：your_wechat_id",
                    is_default=True
                ),
                Template(
                    name="首次触达-简洁版",
                    content="您好！我是永劫无间的内容运营，看到您的AI作品很棒，我们有针对AI创作者的合作计划，感兴趣可以加我微信：your_wechat_id 详聊",
                    is_default=False
                ),
                Template(
                    name="跟进话术-未回复",
                    content="Hi {昵称}，之前给您发过合作邀请，不知道您是否感兴趣？我们的计划对AI创作者很友好，详情可以加我微信：your_wechat_id",
                    is_default=False
                )
            ]

            for template in default_templates:
                db.add(template)

            db.commit()
            print("默认话术模板创建完成")

        # 检查是否有默认设置
        security_setting = db.query(Setting).filter(Setting.key == "security_config").first()
        if not security_setting:
            # 创建默认安全策略
            default_security = {
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

            setting = Setting(
                key="security_config",
                value=json.dumps(default_security),
                description="安全防护策略配置"
            )
            db.add(setting)
            db.commit()
            print("默认安全策略创建完成")

    finally:
        db.close()


@app.get("/")
def read_root():
    """根路径"""
    return {
        "message": "达人猎手 API 服务运行中",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # 运行服务器
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )
