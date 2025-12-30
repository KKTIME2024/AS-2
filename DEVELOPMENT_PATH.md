# VRChat Memory Keeper - 极简可行设计

## 🎯 核心洞察

基于实际可捕获的VRChat数据，系统将记录以下事件：
- 玩家加入/离开某个世界
- 好友加入/离开玩家
- 共同房间事件（玩家-单个好友，开始时间，结束时间）
- 世界属性（名称、标签等）

## 🎪 极简数据模型（4个表）

### 1. 用户表
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(120) NOT NULL
);
```

### 2. 世界表
```sql
CREATE TABLE worlds (
    id INTEGER PRIMARY KEY,
    world_name VARCHAR(200) NOT NULL,
    world_id VARCHAR(100) UNIQUE,
    tags TEXT  -- 简单存储，如"Social,Game,Music"
);
```

### 3. 共同房间事件表（核心业务表）
```sql
CREATE TABLE shared_events (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    friend_name VARCHAR(80) NOT NULL,
    world_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration INTEGER,  -- 秒
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (world_id) REFERENCES worlds(id)
);
```

### 4. 事件-标签关联表（实现多对多）
```sql
CREATE TABLE event_tags (
    event_id INTEGER,
    tag_name VARCHAR(50),
    PRIMARY KEY (event_id, tag_name)
);
```

## 🎨 界面设计（3个核心页面）

### 1. 登录/注册页
- 最简单的表单
- 错误提示
- 响应式设计

### 2. 时间线主页
```html
<div class="event-card">
    <h5>与 Alice 在 The Black Cat</h5>
    <p>⏰ 20:30 - 22:15 (1小时45分钟)</p>
    <p>🏷️ 标签:
        <span class="tag">Social</span>
        <span class="tag">Music</span>
    </p>
    <button class="like-btn" data-event-id="1">
        👍 <span class="like-count">5</span>
    </button>
</div>
```

### 3. 事件详情页
- 完整事件信息
- 标签管理
- 点赞和备注

## 🔧 模拟数据生成

```python
# 简单模拟数据
def generate_mock_data():
    worlds = [
        {"id": 1, "name": "The Black Cat", "tags": "Social,Music,Dance"},
        {"id": 2, "name": "Murder 4", "tags": "Game,Horror"},
    ]
    
    friends = ["Alice", "Bob", "Charlie", "Diana"]
    
    events = []
    for i in range(10):
        start = datetime.now() - timedelta(days=random.randint(0, 30))
        duration = random.randint(300, 7200)  # 5分钟到2小时
        end = start + timedelta(seconds=duration)
        
        events.append({
            "friend": random.choice(friends),
            "world": random.choice(worlds),
            "start_time": start,
            "end_time": end,
            "duration": duration
        })
    
    return worlds, events
```

## 🎯 满足作业要求

| 作业要求 | 本项目实现 | 说明 |
|----------|------------|------|
| ✅ 用户认证 | 注册/登录/登出 | Flask-Login |
| ✅ 多对多关系 | 事件-标签关联 | 用户为事件添加多个标签 |
| ✅ 高级功能 | AJAX点赞 | 无刷新更新点赞数 |
| ✅ 响应式设计 | Bootstrap 5 | 自动适配 |
| ✅ 可访问性 | 语义化HTML | 基础合规 |
| ✅ 本地数据库 | SQLite | 无外部依赖 |

## 💡 这个设计为什么可行？

1. **数据结构真实** - 基于实际可捕获的VRChat数据
2. **复杂度可控** - 只有4个表，关系清晰
3. **时间可管理** - 15小时内可完成核心功能
4. **价值明确** - 记录和回顾共同游戏时光
5. **扩展性强** - 未来可集成真实API

## 📁 项目目录结构

```
VRChat-Memory-Keeper/
├── app.py                     # 应用入口和核心逻辑
├── static/                    # 静态资源
│   ├── css/
│   │   └── main.css           # 主样式
│   └── js/
│       └── main.js            # 主脚本
├── templates/                 # 模板文件
│   ├── base.html              # 基础模板
│   ├── login.html             # 登录页
│   ├── register.html          # 注册页
│   ├── index.html             # 时间线主页
│   └── event_detail.html      # 事件详情页
└── README.md                  # 项目说明
```

## 🌐 路由设计

| 路由 | 方法 | 功能 | 认证要求 |
|------|------|------|----------|
| / | GET | 时间线主页 | 是 |
| /event/<int:event_id> | GET | 事件详情页 | 是 |
| /login | GET/POST | 登录 | 否 |
| /register | GET/POST | 注册 | 否 |
| /logout | GET | 登出 | 是 |
| /api/event/<int:event_id>/like | POST | AJAX点赞 | 是 |
| /event/<int:event_id>/tags | POST | 添加标签 | 是 |

## 🛠️ 技术栈

- **后端**：Flask (Python)
- **数据库**：SQLite
- **ORM**：SQLAlchemy
- **认证**：Flask-Login
- **前端**：HTML5, CSS3, JavaScript (ES6+)
- **样式框架**：Bootstrap 5
- **部署**：PythonAnywhere

## 🎯 核心功能实现

### 用户认证
- 使用Flask-Login实现用户认证
- 密码使用简单存储（demo阶段）
- 登录/注册/登出功能

### 共同房间事件
- 事件时间线展示
- 事件详情查看
- 事件添加备注

### 标签系统
- 世界自带标签
- 用户可添加自定义标签
- 标签筛选功能

### AJAX功能
- 点赞功能，无刷新更新
- 添加标签功能

## 📊 数据统计（可选）

- 与每个好友的共同游戏时长
- 访问最多的世界
- 总游戏时长

## 🎨 主题设计

- 使用Bootstrap 5的默认主题
- 简洁明了的卡片设计
- 响应式布局，适配不同设备

## 🔒 安全性考虑

- 使用Flask-Login保护路由
- SQLAlchemy防止SQL注入
- 基础的输入验证
- 错误信息处理

## 🚀 部署说明

1. **本地开发**：
   - 安装依赖：`pip install flask flask-login flask-sqlalchemy`
   - 运行应用：`python app.py`
   - 访问：http://localhost:5000

2. **PythonAnywhere部署**：
   - 创建PythonAnywhere账户
   - 上传代码
   - 配置WSGI文件
   - 运行数据库迁移
   - 访问分配的URL

## 📝 测试计划

- 手动测试核心功能
- 测试不同浏览器兼容性
- 测试移动端适配
- 测试错误处理

## 🎯 项目目标

创建一个简单、实用的VRChat记忆记录应用，能够记录和展示与好友在不同世界的共同游戏事件，并支持标签管理和点赞功能。

## 开发计划
第1天（5小时）：搭建基础框架

创建项目结构（30分钟）

配置Flask+SQLite（1小时）

实现用户认证（2小时）

创建基础模板（1.5小时）

第2天（6小时）：核心功能 
数据库模型实现（1小时）

时间线页面（2小时）

AJAX点赞功能（1.5小时）

标签系统（1.5小时）

第3天（4小时）：完善部署

样式优化（1小时）

模拟数据生成（1小时）

部署测试（2小时）

## PythonAnywhere部署待办列表

1. ✅ 创建项目部署所需文件
   - requirements.txt - 依赖管理
   - wsgi.py - WSGI配置
   - README.md - 部署指南

2. 📋 PythonAnywhere部署步骤
   - [ ] 创建PythonAnywhere账户
   - [ ] 上传项目文件到PythonAnywhere
   - [ ] 在PythonAnywhere上创建和配置虚拟环境
   - [ ] 安装requirements.txt中的依赖
   - [ ] 配置WSGI文件
   - [ ] 测试部署的应用

3. 🚀 部署后的测试
   - [ ] 访问应用URL确认部署成功
   - [ ] 测试登录/注册功能
   - [ ] 测试时间线显示
   - [ ] 测试点赞功能
   - [ ] 测试标签添加功能

4. 📝 后续维护
   - [ ] 定期备份数据库
   - [ ] 监控应用性能
   - [ ] 处理潜在的安全更新

💡 关键成功因素
1. 严格功能范围控制

只实现作业要求的核心功能

避免"锦上添花"的特性

每个功能都有明确的评分对应

2. 模块化开发

按功能模块分别实现

每个模块完成后立即测试

避免复杂的功能依赖

3. 早期部署测试

第2天就尝试部署到PythonAnywhere

提前发现部署问题

确保最终提交前系统稳定