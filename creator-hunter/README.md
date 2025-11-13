# Creator Hunter (达人猎手)

AIGC达人自动化建联工具 - 高效管理和联系创作者的一站式解决方案

## 📋 项目简介

Creator Hunter 是一个专为AIGC内容运营团队设计的自动化建联工具，旨在提升招募效率5-10倍，将每日触达量从20人提升到100-200人。

### 核心功能

- ✅ **目标管理** - 手动/批量导入创作者信息，智能筛选和去重
- ✅ **话术管理** - 模板库、变量替换、A/B测试
- ✅ **账号管理** - 多账号轮换、健康度监控
- ✅ **自动化发送** - 抖音私信自动化（基于Playwright）
- ✅ **任务调度** - 单条/批量/定时发送，智能频率控制
- ✅ **状态跟踪** - 完整的转化漏斗追踪
- ✅ **数据分析** - 多维度统计分析和可视化

## 🏗️ 技术架构

### 后端
- **FastAPI** - 高性能Web框架
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和消息队列
- **Celery** - 异步任务调度
- **Playwright** - 浏览器自动化
- **SQLAlchemy** - ORM

### 前端
- **React 18** - UI框架
- **Ant Design** - 组件库
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Recharts** - 数据可视化

### 部署
- **Docker** - 容器化
- **Docker Compose** - 多容器编排
- **Nginx** - 静态文件服务和反向代理

## 📦 项目结构

```
creator-hunter/
├── backend/                 # 后端代码
│   ├── app/
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── api/             # API路由
│   │   ├── automation/      # 自动化引擎
│   │   ├── tasks/           # Celery任务
│   │   ├── utils/           # 工具类
│   │   ├── config.py        # 配置
│   │   ├── database.py      # 数据库连接
│   │   └── main.py          # 主应用
│   ├── requirements.txt     # Python依赖
│   └── Dockerfile           # 后端Docker配置
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 公共组件
│   │   ├── services/        # API服务
│   │   ├── App.tsx          # 主应用
│   │   └── main.tsx         # 入口文件
│   ├── package.json         # npm依赖
│   ├── Dockerfile           # 前端Docker配置
│   └── nginx.conf           # Nginx配置
├── docker-compose.yml       # Docker Compose配置
├── .env.example             # 环境变量模板
└── README.md                # 项目文档
```

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (仅开发环境)
- Python 3.11+ (仅开发环境)

### 使用Docker部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd creator-hunter
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，修改必要的配置
```

3. **启动所有服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 本地开发

#### 后端开发

1. **创建虚拟环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. **安装依赖**
```bash
pip install -r requirements.txt
playwright install chromium
```

3. **配置数据库**
```bash
# 确保PostgreSQL和Redis已运行
# 创建数据库
createdb creator_hunter
```

4. **运行后端**
```bash
uvicorn app.main:app --reload
```

5. **运行Celery Worker**
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

6. **运行Celery Beat**
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

#### 前端开发

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **运行开发服务器**
```bash
npm run dev
```

3. **访问**
- http://localhost:3000

## 📖 使用指南

### 1. 添加账号

首次使用需要添加抖音账号：

1. 进入"账号管理"页面
2. 点击"添加账号"
3. 手动登录抖音网页版，导出Cookie
4. 填写账号信息和Cookie
5. 设置每日发送上限

### 2. 创建话术模板

1. 进入"话术管理"页面
2. 点击"新建话术"
3. 填写模板内容，可使用变量：
   - `{昵称}` - 创作者昵称
   - `{粉丝数}` - 粉丝数量
   - `{微信号}` - 对应微信号
   - 更多变量...

### 3. 导入目标创作者

**方式一：手动添加**
1. 进入"目标管理"页面
2. 点击"添加目标"
3. 填写创作者信息

**方式二：批量导入**
1. 下载Excel模板
2. 按照模板填写创作者信息
3. 点击"批量导入"上传文件

### 4. 发送私信

**单条发送**
1. 在目标列表中选择创作者
2. 点击"发送私信"
3. 选择话术模板
4. 确认发送

**批量发送**
1. 筛选目标创作者
2. 勾选多个目标
3. 点击"批量发送"
4. 配置发送策略（间隔、账号轮换等）
5. 开始发送

### 5. 查看数据分析

进入"数据分析"页面，查看：
- 转化漏斗
- 话术效果对比
- 最佳发送时间分析
- 粉丝量段转化率

## ⚠️ 重要提示

### 合规性风险

- 自动化工具违反抖音等平台的服务条款
- 存在账号被封风险
- 建议谨慎使用，做好降级方案
- 仅供内部使用，不对外销售

### 安全建议

1. **频率控制**
   - 单账号每日不超过50条
   - 发送间隔30-90秒随机
   - 定期暂停休息

2. **账号管理**
   - 使用多个账号轮换
   - 监控账号健康度
   - 及时更换异常账号

3. **数据安全**
   - Cookie加密存储
   - 定期备份数据
   - 不泄露敏感信息

## 🔧 配置说明

### 环境变量

```bash
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/creator_hunter

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# 安全
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# 自动化配置
HEADLESS_BROWSER=True
DEFAULT_MESSAGE_INTERVAL_MIN=30
DEFAULT_MESSAGE_INTERVAL_MAX=90

# 限制
MAX_MESSAGES_PER_HOUR=50
MAX_MESSAGES_PER_DAY=200
```

## 📊 数据库Schema

核心数据表：
- `targets` - 目标创作者
- `templates` - 话术模板
- `accounts` - 账号管理
- `messages` - 私信记录
- `tasks` - 发送任务

详见 `backend/app/models/`

## 🛠️ API文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 测试

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 📝 开发计划

### MVP版本 (v1.0) ✅
- [x] 基础架构
- [x] 目标管理
- [x] 话术管理
- [x] 账号管理
- [x] 抖音自动化
- [x] 批量发送
- [x] 数据统计

### V2.0 计划
- [ ] 小红书支持
- [ ] B站支持
- [ ] 自动回复监测
- [ ] AI话术优化
- [ ] 高级数据分析
- [ ] 移动端支持

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目仅供学习和内部使用。

## 📞 联系方式

如有问题，请联系项目负责人。

---

**⚠️ 免责声明**

本工具仅用于学习和研究目的。使用本工具可能违反目标平台的服务条款，使用者需自行承担风险。开发者不对任何损失负责。
