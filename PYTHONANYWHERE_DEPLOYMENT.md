# PythonAnywhere 部署指南

## 当前问题
1. **虚拟环境版本不匹配**：虚拟环境使用 Python 3.10，但 PythonAnywhere 配置使用 Python 3.13
2. **WSGI 配置需要更新**：需要确保 WSGI 配置文件正确指向项目
3. **依赖需要安装**：确保所有依赖都已正确安装在虚拟环境中

## 修复步骤

### 步骤 1: 修复虚拟环境 Python 版本

在 PythonAnywhere 控制台中执行以下命令：

```bash
# 删除旧的虚拟环境
rm -rf /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER

# 创建新的虚拟环境（使用 Python 3.13）
python3.13 -m venv /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER

# 激活虚拟环境
source /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER/bin/activate

# 安装依赖
cd /home/KKTIME2024/AS-2
pip install -r requirements.txt
```

### 步骤 2: 更新 WSGI 配置

登录 PythonAnywhere 管理界面，进入 Web 选项卡，编辑 WSGI 配置文件 `/var/www/kktime2024_pythonanywhere_com_wsgi.py`，将内容替换为：

```python
import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, '/home/KKTIME2024/AS-2')

# Set the Flask application
from app import app as application

# Make sure the instance folder exists
instance_path = os.path.join('/home/KKTIME2024/AS-2', 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-production-secret-key-here'
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/KKTIME2024/AS-2/instance/vrchat_memories.db'
```

### 步骤 3: 配置静态文件

确保静态文件映射正确：
- URL: `/static/`
- 目录: `/home/KKTIME2024/AS-2/static/`

### 步骤 4: 初始化数据库

在 PythonAnywhere 控制台中执行：

```bash
# 激活虚拟环境
source /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER/bin/activate

# 进入项目目录
cd /home/KKTIME2024/AS-2

# 初始化数据库
python -c "from app import app, db; with app.app_context(): db.create_all()"

# 可选：生成测试数据
python -c "from app import app, db; with app.app_context(): init_data()"
```

### 步骤 5: 重新加载应用

**注意**：PythonAnywhere 免费账户不支持 CLI 工具，需要通过网页界面重启应用。

1. 登录到 PythonAnywhere 管理界面
2. 进入 **Web** 选项卡
3. 点击 "Reload" 按钮重新加载应用

## 检查状态

### 查看日志
如果遇到问题，检查以下日志文件：

```bash
# 查看错误日志
tail -n 50 /var/log/kktime2024.pythonanywhere.com.error.log

# 实时监控错误日志
tail -f /var/log/kktime2024.pythonanywhere.com.error.log

# 查看访问日志
tail -n 50 /var/log/kktime2024.pythonanywhere.com.access.log
```

### 验证部署
访问 `https://kktime2024.pythonanywhere.com` 检查应用是否正常运行。

### 数据库验证

```bash
# 检查数据库文件是否存在
ls -la /home/KKTIME2024/AS-2/instance/

# 查看数据库中的表结构
sqlite3 /home/KKTIME2024/AS-2/instance/vrchat_memories.db ".tables"
```

## 常见问题

### 1. 模块导入错误
如果出现 "ModuleNotFoundError"，确保：
- 虚拟环境已激活
- 依赖已正确安装：`pip install -r requirements.txt`
- 项目目录已添加到 Python 路径

### 2. 数据库错误
如果出现数据库相关错误，确保：
- `instance` 目录存在且可写
- `SQLALCHEMY_DATABASE_URI` 配置正确
- 已执行 `db.create_all()` 初始化数据库

### 3. 静态文件不加载
确保静态文件映射已正确配置并已重新加载应用。

### 4. "pythonanywhere: command not found" 错误
PythonAnywhere 免费账户不支持 CLI 工具，所有操作需要通过网页界面完成。

## 定期维护

- 每 3 个月登录一次 PythonAnywhere 并点击 "Run until 3 months from today" 按钮以保持免费网站运行
- 定期检查日志以发现和解决问题
- 更新依赖时重新部署应用

## 修复后的数据库初始化命令

### 正确的数据库初始化命令

```bash
# 进入项目目录
cd /home/KKTIME2024/AS-2

# 激活虚拟环境
source /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER/bin/activate

# 使用正确的多行语法初始化数据库
python - << 'EOF'
from app import app, db
with app.app_context():
    db.create_all()
EOF
```
