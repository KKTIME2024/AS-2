# PythonAnywhere部署指南

## 1. 问题分析
根据您提供的PythonAnywhere仪表盘信息，当前存在一个主要问题：
- 虚拟环境 `/home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER` 使用的是 Python 3.10
- 但Web应用配置的是 Python 3.13
- 这导致了虚拟环境设置问题，需要重新创建正确版本的虚拟环境

## 2. 解决方案步骤

### 步骤1：登录PythonAnywhere控制台
1. 访问 [PythonAnywhere](https://www.pythonanywhere.com/)
2. 登录您的账号 `KKTIME2024`
3. 点击顶部导航栏的 "Consoles" 选项
4. 选择 "Bash" 控制台

### 步骤2：创建正确Python版本的虚拟环境
在Bash控制台中执行以下命令：

```bash
# 删除旧的虚拟环境（可选，如果想保留旧环境可以跳过）
rm -rf /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER

# 创建新的虚拟环境，指定Python 3.13版本
mkvirtualenv --python=/usr/bin/python3.13 VRC-MEM-KEEPER

# 激活虚拟环境
source /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER/bin/activate
```

### 步骤3：安装项目依赖

```bash
# 进入项目目录
cd /home/KKTIME2024/AS-2

# 安装requirements.txt中的依赖
pip install -r requirements.txt
```

### 步骤4：配置WSGI文件

1. 回到PythonAnywhere仪表盘
2. 点击顶部导航栏的 "Web" 选项
3. 找到 "WSGI configuration file"，点击链接 `/var/www/kktime2024_pythonanywhere_com_wsgi.py`
4. 确保WSGI文件内容正确，应该类似于：

```python
import sys
import os

# 加入项目路径
path = '/home/KKTIME2024/AS-2'
if path not in sys.path:
    sys.path.append(path)

# 设置环境变量
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'
os.environ['SECRET_KEY'] = 'your-secret-key-here'  # 替换为您的密钥

# 导入Flask应用
from app import app as application
```

### 步骤5：重新加载Web应用

1. 回到PythonAnywhere仪表盘的Web应用页面
2. 点击页面顶部的 "Reload kktime2024.pythonanywhere.com" 按钮
3. 等待几秒钟，系统会重新加载您的应用

### 步骤6：检查虚拟环境配置

1. 回到Web应用配置页面
2. 找到 "Virtualenv" 部分
3. 确认虚拟环境路径为 `/home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER`
4. 确认不再显示Python版本不匹配的错误

### 步骤7：验证部署

1. 打开浏览器，访问 `https://kktime2024.pythonanywhere.com`
2. 检查应用是否正常运行
3. 如果遇到问题，查看日志文件：
   - Access log: `kktime2024.pythonanywhere.com.access.log`
   - Error log: `kktime2024.pythonanywhere.com.error.log`
   - Server log: `kktime2024.pythonanywhere.com.server.log`

## 3. 常见问题排查

### 问题1：虚拟环境创建失败
- 确保Python 3.13路径正确：`/usr/bin/python3.13`
- 检查磁盘空间是否充足
- 尝试使用 `python3.13 -m venv /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER` 命令创建虚拟环境

### 问题2：依赖安装失败
- 确保虚拟环境已正确激活
- 尝试更新pip：`pip install --upgrade pip`
- 检查requirements.txt文件是否有语法错误

### 问题3：应用无法访问
- 检查WSGI文件配置是否正确
- 查看错误日志，寻找具体错误信息
- 确保静态文件路径配置正确

### 问题4：数据库连接问题
- 如果使用SQLite，确保数据库文件路径正确
- 如果使用其他数据库，确保连接字符串配置正确

## 4. 维护与更新

### 定期更新
1. 登录PythonAnywhere控制台
2. 拉取最新代码：
   ```bash
   cd /home/KKTIME2024/AS-2
   git pull origin main
   ```
3. 激活虚拟环境并更新依赖：
   ```bash
   source /home/KKTIME2024/.virtualenvs/VRC-MEM-KEEPER/bin/activate
   pip install -r requirements.txt
   ```
4. 重新加载Web应用

### 保持应用活跃
- 免费账号需要每3个月登录一次，点击 "Run until 3 months from today" 按钮
- 系统会在到期前一周发送提醒邮件

## 5. 高级配置

### 添加自定义域名
1. 购买域名并配置DNS记录指向PythonAnywhere
2. 在PythonAnywhere仪表盘添加自定义域名
3. 等待HTTPS证书自动配置

### 设置环境变量
- 在WSGI文件中添加环境变量
- 或使用 `.env` 文件（需要安装 `python-dotenv` 库）

### 配置数据库备份
- 定期备份数据库文件
- 对于SQLite，直接复制 `.db` 文件
- 对于其他数据库，使用数据库特定的备份命令

## 6. 联系支持

如果遇到无法解决的问题：
1. 查看PythonAnywhere [帮助文档](https://help.pythonanywhere.com/)
2. 访问PythonAnywhere [论坛](https://www.pythonanywhere.com/forums/)
3. 联系PythonAnywhere支持团队

## 7. 部署完成检查清单

- [ ] 虚拟环境创建成功，Python版本正确
- [ ] 依赖安装完成
- [ ] WSGI文件配置正确
- [ ] Web应用重新加载
- [ ] 应用可以正常访问
- [ ] 静态文件可以正常加载
- [ ] 数据库连接正常
- [ ] 错误日志无严重错误

祝您部署顺利！