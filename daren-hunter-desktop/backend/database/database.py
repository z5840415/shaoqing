from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from pathlib import Path
from .models import Base

# 获取用户数据目录
def get_data_dir():
    """获取数据存储目录"""
    if os.name == 'nt':  # Windows
        data_dir = Path(os.getenv('LOCALAPPDATA')) / 'DarenHunter'
    else:  # macOS/Linux
        data_dir = Path.home() / '.daren-hunter'

    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


# 数据库文件路径
DATABASE_PATH = get_data_dir() / 'data.db'
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print(f"数据库初始化完成，位置: {DATABASE_PATH}")


def get_db():
    """获取数据库会话的依赖注入函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
