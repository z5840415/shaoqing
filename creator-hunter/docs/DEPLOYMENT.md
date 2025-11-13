# 部署指南

## 生产环境部署

### 1. 服务器要求

**最低配置**
- CPU: 2核
- 内存: 4GB
- 存储: 20GB
- 操作系统: Ubuntu 20.04+ / CentOS 8+

**推荐配置**
- CPU: 4核
- 内存: 8GB
- 存储: 50GB SSD
- 操作系统: Ubuntu 22.04 LTS

### 2. 安装Docker

```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 3. 克隆项目

```bash
git clone <repository-url>
cd creator-hunter
```

### 4. 配置环境变量

```bash
cp .env.example .env
nano .env
```

**生产环境配置示例：**
```env
# 数据库（使用强密码）
DATABASE_URL=postgresql://creator_hunter:STRONG_PASSWORD_HERE@postgres:5432/creator_hunter

# Redis
REDIS_URL=redis://redis:6379/0

# 安全密钥（生成随机密钥）
SECRET_KEY=生成一个长随机字符串
ENCRYPTION_KEY=使用 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 生成

# 生产模式
DEBUG=False
HEADLESS_BROWSER=True

# 限制配置（根据实际调整）
MAX_MESSAGES_PER_HOUR=30
MAX_MESSAGES_PER_DAY=100
```

### 5. 启动服务

```bash
# 构建并启动所有容器
docker-compose up -d

# 查看容器状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
```

### 6. 初始化数据库

数据库表会在应用启动时自动创建。如需手动初始化：

```bash
docker-compose exec backend python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### 7. 验证部署

```bash
# 检查后端健康
curl http://localhost:8000/health

# 访问前端
open http://localhost:3000

# 访问API文档
open http://localhost:8000/docs
```

## 数据备份

### 自动备份脚本

创建备份脚本 `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backup/creator-hunter"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U creator_hunter creator_hunter > $BACKUP_DIR/db_$DATE.sql

# 压缩备份
gzip $BACKUP_DIR/db_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

设置定时任务：
```bash
chmod +x backup.sh
crontab -e
# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

## 监控和日志

### 查看日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f celery-worker

# 最近N行
docker-compose logs --tail=100 backend
```

### 监控容器资源

```bash
# 查看容器资源使用
docker stats

# 查看特定容器
docker stats creator-hunter-backend
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build

# 查看更新后的状态
docker-compose ps
```

## 故障排查

### 容器无法启动

```bash
# 查看容器日志
docker-compose logs backend

# 检查配置
docker-compose config

# 重启服务
docker-compose restart backend
```

### 数据库连接失败

```bash
# 检查数据库容器
docker-compose ps postgres

# 进入数据库容器
docker-compose exec postgres psql -U creator_hunter

# 检查数据库连接
docker-compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

### Celery任务不执行

```bash
# 检查Celery Worker
docker-compose logs celery-worker

# 检查Redis连接
docker-compose exec redis redis-cli ping

# 重启Celery
docker-compose restart celery-worker celery-beat
```

## 性能优化

### 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_targets_status ON targets(status);
CREATE INDEX idx_messages_target_id ON messages(target_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### Redis优化

在 `docker-compose.yml` 中添加Redis配置：

```yaml
redis:
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

## 安全加固

### 1. 使用HTTPS

配置Nginx SSL：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

### 2. 防火墙配置

```bash
# 仅开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 3. 定期更新

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 更新Docker镜像
docker-compose pull
docker-compose up -d
```

## 扩展部署

### 水平扩展Celery Worker

修改 `docker-compose.yml`:

```yaml
celery-worker:
  # ...原有配置
  deploy:
    replicas: 3  # 启动3个Worker实例
```

### 使用外部数据库

修改 `.env`:

```env
DATABASE_URL=postgresql://user:password@external-db-host:5432/creator_hunter
```

## 联系支持

如遇到部署问题，请联系技术支持团队。
