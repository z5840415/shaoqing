# 达人猎手 - AIGC达人自动化建联工具

## 项目简介

达人猎手是一款桌面应用，用于自动化批量发送抖音私信，帮助运营团队高效招募AIGC达人。

**核心功能：**
- 批量导入达人信息（Excel）
- 话术库管理和模板化发送
- 自动化私信发送（基于Playwright）
- 发送进度实时监控
- 数据统计和效果分析
- 安全防护策略（频率控制、行为模拟）

## 技术架构

- **前端**: Electron + HTML/CSS/JavaScript
- **后端**: Python + FastAPI
- **数据库**: SQLite
- **自动化**: Playwright
- **打包**: electron-builder

## 开发环境搭建

### 前置要求

- Node.js 16+
- Python 3.9+
- npm 或 yarn

### 安装步骤

1. **克隆项目**
```bash
cd daren-hunter-desktop
```

2. **安装Node.js依赖**
```bash
npm install
```

3. **安装Python依赖**
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
cd ..
```

4. **启动开发环境**

方式1：同时启动前后端
```bash
npm run dev
```

方式2：分别启动
```bash
# 终端1：启动后端
cd backend
python main.py

# 终端2：启动前端
npm start
```

## 使用指南

### 1. 首次配置

#### 1.1 配置抖音Cookie

1. 在浏览器中登录 `douyin.com`
2. 按F12打开开发者工具
3. 切换到Console（控制台）标签
4. 输入并执行：`document.cookie`
5. 复制输出的Cookie字符串
6. 在应用的"设置"页面粘贴Cookie并保存

#### 1.2 创建话术模板

1. 进入"话术库"页面
2. 点击"新建话术"
3. 输入话术名称和内容
4. 支持变量：`{昵称}` `{粉丝数}` `{微信号}`等
5. 保存并设为默认（可选）

### 2. 导入达人

#### 2.1 下载导入模板

1. 进入"达人管理"页面
2. 点击"下载模板"
3. 在Excel中填写达人信息

**模板字段说明：**
- 昵称*（必填）
- 抖音ID*（必填）
- 主页链接
- 粉丝数
- 标签（多个用逗号分隔）
- 备注

#### 2.2 导入Excel

1. 点击"导入Excel"
2. 选择填好的Excel文件
3. 系统自动去重并导入

### 3. 批量发送

#### 3.1 选择目标

1. 在达人列表中勾选需要发送的达人
2. 点击"批量发送"

#### 3.2 配置发送

1. 选择话术模板
2. 设置发送策略（立即/定时）
3. 配置安全参数：
   - 发送间隔：30-60秒（推荐）
   - 批次大小：30条
   - 批次休息：10分钟
   - 每日上限：100条

#### 3.3 开始发送

1. 点击"开始发送"
2. 查看实时进度
3. 可暂停/停止发送

### 4. 数据统计

- 查看今日/本周/本月的发送和回复统计
- 对比不同话术的效果
- 分析最佳发送时间
- 导出统计报表

## 安全策略说明

### 推荐配置（标准模式）

- **发送间隔**: 30-60秒随机
- **批次大小**: 30条
- **批次休息**: 10分钟
- **每日上限**: 100条
- **夜间暂停**: 开启（23:00-7:00）
- **行为模拟**: 全部开启

### 防封号建议

1. **频率控制**: 不要设置过于激进的间隔
2. **多账号策略**: 准备2-3个账号轮换使用
3. **观察反馈**: 如果出现限流，立即降低频率
4. **人工介入**: 定期手动回复一些消息
5. **Cookie更新**: 定期更新Cookie（建议每周）

## 打包发布

### Windows打包

```bash
npm run build:win
```

生成文件位于 `dist/达人猎手 Setup.exe`

### macOS打包

```bash
npm run build:mac
```

生成文件位于 `dist/达人猎手.dmg`

## 项目结构

```
daren-hunter-desktop/
├── frontend/                 # 前端Electron应用
│   ├── index.html           # 主页面
│   ├── main.js              # Electron主进程
│   ├── styles/              # 样式文件
│   │   └── main.css
│   └── scripts/             # 前端脚本
│       ├── api.js           # API封装
│       ├── utils.js         # 工具函数
│       ├── targets.js       # 达人管理
│       ├── templates.js     # 话术库
│       ├── send.js          # 发送任务
│       ├── statistics.js    # 数据统计
│       ├── settings.js      # 设置
│       └── main.js          # 主控制
├── backend/                 # Python后端
│   ├── main.py             # FastAPI主程序
│   ├── schemas.py          # 数据模型
│   ├── requirements.txt    # Python依赖
│   ├── database/           # 数据库
│   │   ├── models.py       # ORM模型
│   │   └── database.py     # 数据库配置
│   ├── routers/            # API路由
│   │   ├── targets.py      # 达人管理API
│   │   ├── templates.py    # 话术管理API
│   │   ├── send.py         # 发送任务API
│   │   ├── statistics.py   # 统计API
│   │   └── settings.py     # 设置API
│   └── services/           # 业务逻辑
│       └── douyin_sender.py # 抖音发送器
├── package.json            # Node.js配置
└── README.md              # 说明文档
```

## API文档

启动后端服务后，访问 http://127.0.0.1:8000/docs 查看完整API文档。

## 常见问题

### Q1: Cookie失效怎么办？

**A**: Cookie有效期通常为30天，失效后需要重新获取：
1. 重新登录抖音网页版
2. 按照"配置抖音Cookie"步骤重新获取
3. 在设置页面更新Cookie

### Q2: 发送失败是什么原因？

**A**: 可能的原因：
- Cookie失效 → 重新配置Cookie
- 网络问题 → 检查网络连接
- 被限流 → 降低发送频率，休息后再试
- 页面结构变化 → 联系开发者更新

### Q3: 如何提高回复率？

**A**: 建议：
1. 优化话术内容，更个性化
2. 选择合适的发送时间（14:00-17:00效果最好）
3. 精准筛选目标达人
4. 及时跟进回复的用户

### Q4: 会不会被封号？

**A**: 采取以下措施降低风险：
- 使用推荐的安全配置
- 不要过度频繁发送
- 开启所有行为模拟功能
- 准备多个账号轮换

### Q5: 数据存储在哪里？

**A**:
- Windows: `C:\Users\[用户名]\AppData\Local\DarenHunter\data.db`
- macOS: `~/.daren-hunter/data.db`

## 更新日志

### v1.0.0 (2024-01-XX)

- ✅ 达人批量导入和管理
- ✅ 话术库管理
- ✅ 自动化批量发送
- ✅ 实时进度监控
- ✅ 数据统计分析
- ✅ 安全防护策略

## 许可证

本项目仅供学习和内部使用，请遵守平台规则，合理使用自动化工具。

## 联系方式

如有问题或建议，请联系开发团队。

---

**免责声明**: 本工具仅用于提高工作效率，使用者需自行承担使用风险，开发者不对任何后果负责。请遵守相关平台的使用条款和法律法规。
