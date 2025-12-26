# Git多人协作开发指南 - VRChat Memory Keeper

## 🌿 Git分支策略

### 主分支结构
```
main (稳定版本)
├── develop (开发分支)
│   ├── feature/init-project (项目初始化分支)
│   ├── feature/flask-sqlite-setup (Flask+SQLite配置分支)
│   ├── feature/user-auth (用户认证分支)
│   ├── feature/base-templates (基础模板分支)
│   ├── feature/db-models (数据库模型分支)
│   ├── feature/timeline-page (时间线页面分支)  
│   ├── feature/ajax-likes (AJAX点赞功能分支)
│   └── feature/tags-system (标签系统分支)
└── release/v1.0.0 (版本发布分支)
```

### 分支命名规范
- **main**: 主分支，包含稳定可部署的代码
- **develop**: 开发分支，集成所有已完成的功能
- **feature/***: 功能分支，用于开发具体功能
- **bugfix/***: 修复分支，用于修复生产环境bug
- **release/***: 发布分支，用于准备发布版本

## 👥 团队成员与任务分配

| 成员 | 角色 | 负责功能 | 对应分支 | 时间分配 |
|------|------|----------|----------|----------|
| 张三 | 前端开发 | 基础模板、页面设计 | feature/base-templates | 1.5小时 |
| 李四 | 后端开发 | Flask+SQLite配置、数据库模型 | feature/flask-sqlite-setup, feature/db-models | 2小时 |
| 王五 | 全栈开发 | 用户认证、时间线页面 | feature/user-auth, feature/timeline-page | 4小时 |
| 赵六 | 前端开发 | AJAX点赞功能、标签系统 | feature/ajax-likes, feature/tags-system | 3小时 |
| 钱七 | DevOps | 部署、测试 | release/v1.0.0 | 2小时 |

## 📋 开发流程

### 1. 初始化开发环境
```bash
git clone <repository-url>
cd VRChat-Memory-Keeper
pip install flask flask-login flask-sqlalchemy
```

### 2. 创建功能分支
从develop分支创建新的功能分支：
```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### 3. 开发与提交
- 遵循代码规范
- 定期提交代码（每个功能点至少一个提交）
- 提交信息遵循规范

### 4. 提交规范
提交信息格式：
```
<类型>: <简短描述>

[可选] 详细描述

[可选] 关联Issue: #123
```

类型包括：
- feat: 新功能
- fix: 修复bug
- docs: 文档修改
- style: 代码格式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建或工具相关

示例：
```
feat: 实现用户登录功能

- 添加登录路由和模板
- 集成Flask-Login认证
- 实现登录表单验证

关联Issue: #1
```

### 5. 代码审查与合并
1. 开发完成后，推送分支到远程仓库
2. 创建Pull Request (PR) 到develop分支
3. 至少1名团队成员进行代码审查
4. 审查通过后，合并到develop分支
5. 删除远程功能分支

### 6. 发布流程
1. 从develop分支创建release分支
2. 进行最终测试和bug修复
3. 合并到main分支
4. 打标签并发布
5. 合并回develop分支

## 🚨 冲突解决

1. 拉取最新代码：`git pull origin develop`
2. 查看冲突文件：`git status`
3. 手动解决冲突
4. 标记冲突已解决：`git add <冲突文件>`
5. 完成合并：`git commit -m "fix: 解决合并冲突"`

## 📊 开发进度跟踪

### 第1天（5小时）：搭建基础框架
- ✅ feature/init-project (30分钟) - 完成
- ✅ feature/flask-sqlite-setup (1小时) - 完成
- ✅ feature/user-auth (2小时) - 完成
- ✅ feature/base-templates (1.5小时) - 完成

### 第2天（6小时）：核心功能
- ✅ feature/db-models (1小时) - 完成
- ✅ feature/timeline-page (2小时) - 完成
- ✅ feature/ajax-likes (1.5小时) - 完成
- ✅ feature/tags-system (1.5小时) - 完成

### 第3天（4小时）：完善部署
- ✅ release/v1.0.0 (2小时) - 完成
- ✅ 样式优化 (1小时) - 完成
- ✅ 模拟数据生成 (1小时) - 完成

## 🎯 发布完成

### 已完成的工作
1. ✅ 所有功能分支已合并到develop分支
2. ✅ release/v1.0.0分支已合并到main分支
3. ✅ main分支已打v1.0.0标签
4. ✅ 编写了完整的单元测试
5. ✅ 创建了.gitignore文件
6. ✅ 完成了部署准备

### 后续建议
1. 运行最终测试：`python -m pytest tests/test_app.py -v`
2. 部署到生产环境
3. 开始规划v2.0.0功能

## 📎 代码规范

### Python/Flask规范
- 使用PEP 8代码风格
- 函数和变量使用小写字母+下划线命名
- 类名使用驼峰命名法
- 每个函数和类添加文档字符串
- 使用SQLAlchemy ORM，避免直接写SQL

### HTML/CSS/JS规范
- 使用语义化HTML标签
- CSS使用BEM命名规范
- JS使用ES6+语法
- 使用Bootstrap 5组件和样式
- 保持代码简洁，避免冗余

## 🧪 测试规范

- 每个功能完成后进行手动测试
- 测试不同浏览器兼容性
- 测试移动端适配
- 测试错误处理
- 记录测试结果

## 🚀 部署流程

1. **本地开发测试**：`python app.py`
2. **部署到PythonAnywhere**：
   - 上传代码到PythonAnywhere
   - 配置WSGI文件
   - 安装依赖
   - 运行数据库迁移
3. **访问测试**：检查公网访问是否正常
4. **监控与维护**：定期检查应用状态

## 📈 版本控制

- 遵循语义化版本规范：v<主版本>.<次版本>.<修订版本>
- 主版本：不兼容的API变更
- 次版本：向下兼容的新功能
- 修订版本：向下兼容的bug修复

## 🤝 协作工具

- **代码仓库**：GitHub
- **项目管理**：Trello
- **沟通工具**：Slack
- **代码审查**：GitHub Pull Requests

## 📝 注意事项

1. 每天结束前推送代码到远程仓库
2. 遇到问题及时沟通，避免卡壳
3. 严格遵循分支策略和命名规范
4. 保持代码质量，编写清晰的注释
5. 定期更新本地分支，避免冲突

## 🏆 团队目标

创建一个简单、实用的VRChat记忆记录应用，能够记录和展示与好友在不同世界的共同游戏事件，并支持标签管理和点赞功能。在15小时内完成所有核心功能并成功部署到公网。

## 🚀 具体实施步骤

### 第1步：初始化仓库和基础分支
```bash
# 初始化主仓库
git init
git add .
git commit -m "🎉 初始提交：项目基础结构"

# 创建并切换到认证功能分支
git checkout -b feature/auth
```

### 第2步：模拟开发者Alice - 认证模块 (第1天)
```bash
# Alice在认证分支开发
git checkout feature/auth

# 开发用户认证功能...
# 完成后提交
git add .
git commit -m "✅ 完成用户认证模块：登录/注册/登出"

# 将认证分支推送到远程（模拟多人协作）
git push origin feature/auth
```

### 第3步：模拟开发者Bob - 时间线模块 (同时进行)
```bash
# 在另一个终端或目录，模拟Bob克隆项目
git clone [你的仓库地址] vrchat-bob
cd vrchat-bob

# Bob创建自己的时间线分支
git checkout -b feature/timeline

# 开发时间线功能...
git add .
git commit -m "✅ 完成时间线主页：事件卡片展示"

# Bob推送他的分支
git push origin feature/timeline
```

### 第4步：功能分支合并 (第2天)
```bash
# 回到主分支准备合并
git checkout main

# 合并Alice的认证功能
git merge feature/auth -m "🔗 合并认证功能分支"

# 合并Bob的时间线功能（可能解决冲突）
git merge feature/timeline -m "🔗 合并时间线功能分支"

# 测试合并后的功能
```

### 第5步：继续开发其他功能
```bash
# 创建新功能分支
git checkout -b feature/tags
# 开发标签系统...
git commit -m "✅ 完成标签管理系统"

git checkout -b feature/likes  
# 开发点赞功能...
git commit -m "✅ 完成AJAX点赞功能"
```

## 🔄 模拟的多人协作场景

### 场景1：并行开发不同功能
```bash
# Alice和Bob同时开发不同模块，互不干扰
# Alice: feature/auth → 用户认证
# Bob: feature/timeline → 时间线展示
```

### 场景2：合并冲突解决（重要学习点）
```bash
# 模拟冲突：两人都修改了同一个文件
# Alice修改了app.py的认证部分
# Bob修改了app.py的路由部分

git merge feature/timeline
# 出现冲突！学习解决冲突
```

### 场景3：功能测试和代码审查
```bash
# 创建测试分支
git checkout -b test/integration

# 合并多个功能进行集成测试
git merge feature/auth
git merge feature/timeline
git merge feature/tags

# 测试通过后合并到main
git checkout main
git merge test/integration
```

## 📋 完整的Git工作流程脚本

```bash
#!/bin/bash
# 多人开发模拟脚本

echo "🎯 开始模拟多人Git开发流程..."

# 1. 初始化项目
echo "1. 初始化主仓库..."
git init
git add .
git commit -m "🎉 初始提交：项目基础结构"

# 2. 模拟Alice开发认证功能
echo "2. Alice开发认证模块..."
git checkout -b feature/auth

# 模拟Alice的工作
cat > app.py << 'EOF'
# Alice的认证功能代码
from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)
login_manager = LoginManager(app)

# 认证路由...
EOF

git add app.py
git commit -m "✅ [Alice] 完成用户认证基础框架"

# 3. 模拟Bob开发时间线功能  
echo "3. Bob开发时间线模块..."
git checkout main
git checkout -b feature/timeline

# 模拟Bob的工作
cat > templates/index.html << 'EOF'
<!-- Bob的时间线界面 -->
<div class="timeline">
    <div class="event-card">时间线内容...</div>
</div>
EOF

git add templates/index.html
git commit -m "✅ [Bob] 完成时间线界面设计"

# 4. 合并功能分支
echo "4. 合并功能分支到main..."
git checkout main
git merge feature/auth -m "🔗 合并Alice的认证功能"
git merge feature/timeline -m "🔗 合并Bob的时间线功能"

# 5. 创建发布分支
echo "5. 创建发布版本..."
git checkout -b release/v1.0
git add .
git commit -m "🚀 发布v1.0版本：基础功能完成"

# 合并回main
git checkout main
git merge release/v1.0 -m "🎯 完成v1.0版本发布"

echo "✅ 多人开发模拟完成！"
```

## 🎯 关键Git命令总结

| 场景 | 命令 | 说明 |
|------|------|------|
| 开始新功能 | `git checkout -b feature/xxx` | 创建功能分支 |
| 日常开发 | `git add . && git commit -m "msg"` | 常规提交 |
| 同步上游 | `git fetch origin && git merge main` | 获取最新代码 |
| 解决冲突 | 编辑冲突文件 → `git add` → `git commit` | 冲突处理 |
| 功能完成 | `git checkout main && git merge feature/xxx` | 合并到主分支 |
| 撤销错误 | `git reset --hard HEAD^` | 回退上次提交 |

## 💡 针对作业的优化建议

### 时间分配（15小时总工时）
```
第1天 (5小时):
- 1小时: Git分支设置和基础框架 (main分支)
- 2小时: Alice开发认证功能 (feature/auth)
- 2小时: Bob开发时间线框架 (feature/timeline)

第2天 (6小时):
- 2小时: 合并冲突解决和集成测试
- 2小时: 开发标签功能 (feature/tags)
- 2小时: 开发点赞功能 (feature/likes)

第3天 (4小时):
- 2小时: 最终测试和bug修复
- 2小时: 部署和文档整理
```

## 📌 最佳实践

1. **频繁提交**：每次完成一个小功能就提交，避免大段代码未提交
2. **清晰的提交信息**：使用语义化的提交信息，如 `feat: 完成xxx功能`
3. **定期同步**：定期从主分支拉取最新代码，避免冲突积累
4. **分支命名规范**：使用 `feature/功能名` 格式命名功能分支
5. **代码审查**：合并前进行代码审查，确保代码质量
6. **测试先行**：合并前进行测试，确保功能正常

通过以上练习，你可以掌握Git多人协作的核心概念和操作，为实际开发做好准备！