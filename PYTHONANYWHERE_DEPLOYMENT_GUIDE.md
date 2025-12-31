# PythonAnywhere部署指南

本指南将详细介绍如何将VRChat Memories项目部署到PythonAnywhere平台。

## 1. 登录到PythonAnywhere

1. 访问 [PythonAnywhere](https://www.pythonanywhere.com/)
2. 使用您的账号登录

## 2. 创建新的Web应用

1. 在控制面板中，点击 "Web" 标签
2. 点击 "Add a new web app" 按钮
3. 选择 "Manual configuration"（手动配置）
4. 选择适合的Python版本（建议3.9或更高版本）
5. 点击 "Next" 完成创建

## 3. 克隆GitHub仓库

1. 在控制面板中，点击 "Consoles" 标签
2. 点击 "Bash" 打开一个新的终端
3. 执行以下命令克隆仓库：
   ```bash
   git clone https://github.com/KKTIME2024/AS-2.git
   ```
4. 进入项目目录：
   ```bash
   cd AS-2
   ```

## 4. 设置虚拟环境

1. 创建虚拟环境：
   ```bash
   python -m venv venv
   ```
2. 激活虚拟环境：
   ```bash
   source venv/bin/activate
   ```

## 5. 安装依赖

1. 安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 6. 配置WSGI文件

1. 在PythonAnywhere控制面板中，回到 "Web" 标签
2. 在 "Code" 部分，找到 "WSGI configuration file" 并点击链接打开它
3. 将WSGI文件内容替换为：
   ```python
   import sys
   import os
   
   # 添加项目路径到系统路径
   path = '/home/[your-username]/AS-2'
   if path not in sys.path:
       sys.path.append(path)
   
   # 激活虚拟环境
   activate_this = '/home/[your-username]/AS-2/venv/bin/activate_this.py'
   with open(activate_this) as file_:
       exec(file_.read(), dict(__file__=activate_this))
   
   # 设置环境变量
   os.chdir(path)
   os.environ['FLASK_APP'] = 'app.py'
   os.environ['FLASK_ENV'] = 'production'
   
   # 导入Flask应用
   from app import app as application
   ```
   注意：将 `[your-username]` 替换为您的PythonAnywhere用户名

## 7. 设置数据库

1. 在项目目录中，执行以下命令初始化数据库：
   ```bash
   python -c "from app import app, db; with app.app_context(): db.create_all()"
   ```

## 8. 配置静态文件（可选）

如果您的项目有静态文件，需要在PythonAnywhere中配置：

1. 在 "Web" 标签的 "Static files" 部分，点击 "Add a new static file mapping"
2. 设置URL路径为 `/static/`
3. 设置目录路径为 `/home/[your-username]/AS-2/static`
4. 点击 "Save"

## 9. 重启Web应用

1. 在 "Web" 标签中，点击 "Reload [your-username].pythonanywhere.com"
2. 等待几分钟后，访问您的网站：`https://[your-username].pythonanywhere.com`

## 10. 定期更新部署

当您在本地对项目进行修改并推送到GitHub后，需要在PythonAnywhere上更新：

1. 打开Bash终端
2. 进入项目目录：`cd AS-2`
3. 拉取最新代码：`git pull origin main`
4. 激活虚拟环境：`source venv/bin/activate`
5. 安装新的依赖（如果有）：`pip install -r requirements.txt`
6. 更新数据库（如果有）：`python -c "from app import app, db; with app.app_context(): db.create_all()"`
7. 重启Web应用：在Web标签中点击 "Reload"

## 注意事项

1. 确保在WSGI文件中正确设置了所有路径
2. 首次访问网站时，可能需要等待几分钟才能正常运行
3. 如果遇到问题，可以查看PythonAnywhere的错误日志
4. 建议在生产环境中更改Flask应用的SECRET_KEY

## 常见问题排查

### 1. 网站显示500错误

- 查看错误日志：在Web标签中，找到 "Error log" 并点击查看
- 检查WSGI文件中的路径是否正确
- 确保所有依赖都已正确安装

### 2. 数据库连接错误

- 确保数据库文件路径正确
- 检查数据库初始化命令是否成功执行

### 3. 静态文件无法访问

- 检查静态文件映射是否正确配置
- 确保静态文件存在于指定目录中

## 联系信息

如果您在部署过程中遇到任何问题，请联系项目维护者。
