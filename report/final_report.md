# VRChat 记忆共享平台项目报告

## 1. My Website

VRChat 记忆共享平台是一个专为 VRChat 用户设计的社交应用，旨在帮助用户记录、分享和重温在虚拟世界中的共同经历。该平台允许用户创建事件记录，邀请好友参与，添加评论和标签，并通过可视化方式展示社交互动数据，增强用户之间的连接和回忆。

## 2. User Path

### 典型用户使用流程：记录与朋友的 VRChat 聚会

1. **用户登录**：用户访问网站首页，输入用户名和密码进行登录。
2. **创建新事件**：登录后，用户点击导航栏中的"创建事件"按钮，进入事件创建页面。
3. **填写事件信息**：用户输入事件相关信息，包括：
   - 朋友名称
   - 世界名称
   - 开始和结束时间
   - 添加自定义标签
   - 设置隐私权限
4. **提交事件**：用户点击"保存"按钮，系统创建事件记录并返回事件列表页面。
5. **查看事件详情**：用户点击事件卡片，进入事件详情页面，可以：
   - 查看事件完整信息
   - 添加评论
   - 邀请其他好友参与
   - 编辑或删除事件
6. **浏览活动动态**：用户可以通过"活动动态"页面查看好友的最新活动和事件。

## 3. Design

### 设计选择与原因

- **配色方案**：采用深色主题配合明亮的强调色，符合 VRChat 平台的科技感和沉浸感，同时减轻长时间使用的视觉疲劳。
- **布局结构**：使用响应式设计，确保在不同设备上都能提供良好的用户体验。主要内容区域采用卡片式布局，使信息层次清晰，易于浏览。
- **交互设计**：添加了平滑的过渡动画和悬停效果，提升用户交互体验，同时保持界面简洁直观。

### 设计亮点

- **动态时间线**：事件列表采用时间线式布局，直观展示用户的 VRChat 活动历史。
- **智能搜索功能**：支持多种日期格式和中文自然语言搜索，如"昨天"、"春节"等，提高用户查找事件的效率。
- **数据可视化**：通过图表直观展示用户的社交互动数据，如最常访问的世界、互动最频繁的好友等。

### 技术挑战与解决方案

在开发过程中，最大的挑战是实现智能日期解析功能，支持多种日期格式和中文自然语言查询。

```python
def parse_search_query(search_query):
    """解析搜索查询，提取关键词和日期范围
    采用多模式解析器架构，支持多种日期格式
    """
    keywords = []
    start_date = None
    end_date = None
    
    if not search_query:
        return keywords, start_date, end_date
    
    # 预处理查询
    processed_query, date_keywords = preprocess_query(search_query)
    
    # 分割搜索词
    search_terms = processed_query.split()
    
    # 日期格式正则表达式 - 支持更多格式
    date_patterns = [
        (r'^(\d{4}-\d{1,2}-\d{1,2})$', '%Y-%m-%d'),  # YYYY-MM-DD
        (r'^(\d{4}/\d{1,2}/\d{1,2})$', '%Y/%m/%d'),  # YYYY/MM/DD
        (r'^(\d{4}\.\d{1,2}\.\d{1,2})$', '%Y.%m.%d'),  # YYYY.MM.DD
        # 支持中文日期格式
        (r'^(\d{4})年(\d{1,2})月(\d{1,2})日?$', '%Y-%m-%d'),
        # 支持相对日期和节假日
    ]
    
    # 逐个处理搜索词，识别日期和关键词
    for term in search_terms:
        # 尝试多种日期解析方法
        is_date = False
        # ...（具体解析逻辑）
        
        # 如果不是日期，添加到关键词列表
        if not is_date:
            keywords.append(term)
    
    return keywords, start_date, end_date
```

通过实现多模式解析器架构，系统能够识别并处理多种日期格式，包括标准格式（如YYYY-MM-DD）、中文格式（如2023年12月31日）、相对日期（如昨天、明天）和节假日（如春节、国庆节）。

## 4. Accessibility

为了提升网站的可访问性，我们采取了以下措施：

1. **语义化HTML结构**：使用适当的HTML标签（如`<header>`, `<nav>`, `<main>`, `<section>`）构建页面结构，提高屏幕阅读器的可读性。

2. **键盘导航支持**：确保所有交互元素都可以通过键盘访问，包括表单控件、按钮和链接。

3. **色彩对比度**：确保文本与背景之间有足够的对比度，符合WCAG AA级标准，便于视觉障碍用户阅读。

4. **图片替代文本**：为所有图片添加了`alt`属性，描述图片内容，帮助屏幕阅读器用户理解页面内容。

5. **表单标签**：为所有表单元素添加了明确的标签，提高表单的可访问性。

6. **错误提示**：表单验证错误时，提供清晰的错误信息，并将焦点自动定位到出错的字段。

## 5. Database

### 数据库设计

系统采用SQLite数据库，使用SQLAlchemy ORM进行数据库操作。数据库模型设计支持复杂的多对多关系，主要包括：

1. **用户-好友关系**：通过`user_friends`关联表实现用户之间的好友关系。
2. **事件-参与者关系**：通过`event_participants`关联表实现事件与参与者之间的多对多关系。
3. **事件-标签关系**：通过`EventTag`模型实现事件与自定义标签之间的多对多关系。

### 核心数据库模型

```python
# 用户模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    events = db.relationship('SharedEvent', backref='user', lazy=True)
    friends = db.relationship(
        'User',
        secondary='user_friends',
        primaryjoin='user_friends.c.user_id == User.id',
        secondaryjoin='user_friends.c.friend_id == User.id',
        backref=db.backref('friended_by', lazy='dynamic'),
        lazy='dynamic'
    )

# 事件模型
class SharedEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    friend_name = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 持续时间（秒）
    notes = db.Column(db.Text, nullable=True)  # 事件备注
    privacy = db.Column(db.String(20), default='public')
    custom_tags = db.relationship(
        'EventTag',
        backref='event',
        lazy=True,
        cascade='all, delete-orphan'
    )
    participants = db.relationship(
        'User',
        secondary='event_participants',
        backref=db.backref('participated_events', lazy='dynamic'),
        lazy='dynamic'
    )
```

### 多对多关系的必要性

1. **用户-好友关系**：允许用户与多个其他用户建立好友关系，支持社交网络的核心功能。
2. **事件-参与者关系**：一个事件可以有多个参与者，一个用户可以参与多个事件，实现共享体验的核心功能。
3. **事件-标签关系**：允许为事件添加多个自定义标签，提高事件的可搜索性和组织性。

### 数据库设计对用户体验的影响

良好的数据库设计确保了：
- 高效的数据查询和检索
- 灵活的关系管理
- 数据的完整性和一致性
- 支持复杂的社交功能，如事件共享、好友动态等

## 6. Advanced Feature

### 智能搜索与日期解析

系统实现了高级搜索功能，支持多种日期格式和中文自然语言查询，这是项目的核心高级功能。

#### 实现代码

```python
def parse_chinese_date(text, base_date=None):
    """中文日期识别"""
    # 中文数字映射
    chinese_num_map = {
        '零': 0, '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8, '九': 9
    }
    
    # 中文月份映射
    chinese_month_map = {
        '一': 1, '二': 2, '三': 3, '四': 4,
        '五': 5, '六': 6, '七': 7, '八': 8,
        '九': 9, '十': 10, '十一': 11, '十二': 12
    }
    
    # 解析模式（如"十二月二十五日"）
    pattern3 = r'([\u4e00-\u9fa5]+月)([\u4e00-\u9fa5]+日?)'
    match = re.match(pattern3, text)
    if match:
        month_str, day_str = match.groups()
        month_str = month_str.rstrip('月')
        day_str = day_str.rstrip('日')
        
        month = chinese_month_map.get(month_str, None)
        day = chinese_to_arabic(day_str)
        
        if month and day:
            return datetime(base_date.year, month, day)
    
    return None
```

#### 功能价值

该功能极大提升了用户体验：
- 用户可以使用自然语言查询事件，如"查找昨天和张三的事件"、"搜索春节期间的聚会"
- 支持多种日期格式，满足不同用户的输入习惯
- 提高了搜索效率和准确性，使用户能够快速找到所需的事件记录

## 7. Testing & Critical Analysis

### 7.1 Testing

#### 可访问性测试

- **测试工具**：使用 WAVE 网页可访问性评估工具
- **测试内容**：
  - 语义化HTML结构检查
  - 色彩对比度分析
  - 键盘导航测试
  - 屏幕阅读器兼容性测试
- **测试结果**：网站符合 WCAG AA 级可访问性标准，所有交互元素都支持键盘访问，色彩对比度达标。

#### 功能性测试

- **测试方法**：手动测试结合自动化测试
- **测试内容**：
  - 用户认证功能（注册、登录、登出）
  - 事件创建、编辑、删除功能
  - 好友系统功能
  - 搜索功能（包括各种日期格式测试）
  - 评论和标签功能
- **测试结果**：所有核心功能正常工作，搜索功能能够正确解析各种日期格式和自然语言查询。

#### 布局与响应式设计测试

- **测试设备**：桌面端（1920×1080）、平板（768×1024）、移动端（375×667）
- **测试内容**：
  - 页面布局在不同设备上的显示效果
  - 导航菜单在移动端的适配
  - 事件卡片的响应式调整
- **测试结果**：网站在各种设备上都能提供良好的用户体验，布局自适应不同屏幕尺寸。

### 7.2 Analysis

#### What Went Well

1. **数据库设计**：采用了合理的数据库模型和关系设计，支持复杂的社交功能，数据查询效率高。
2. **智能搜索功能**：成功实现了支持多种日期格式和中文自然语言查询的高级搜索功能，提升了用户体验。
3. **响应式设计**：网站在不同设备上都能提供良好的显示效果，适配性强。
4. **可访问性**：网站符合可访问性标准，确保所有用户都能正常使用。

#### What Went Badly

1. **性能优化**：在数据量较大的情况下，事件列表页面加载速度较慢，需要进一步优化查询性能。
2. **用户界面**：部分页面的交互设计可以进一步改进，如表单验证的即时反馈、加载状态的显示等。
3. **错误处理**：某些错误场景的处理不够完善，如网络连接中断时的用户提示。

#### Improvements

1. **性能优化**：
   - 实现数据库查询缓存机制
   - 优化事件列表的分页加载
   - 使用异步加载技术提升页面响应速度

2. **功能扩展**：
   - 添加文件上传功能，支持用户上传 VRChat 截图和视频
   - 实现事件提醒功能，提前通知用户即将到来的事件
   - 添加社交分享功能，允许用户将事件分享到其他社交平台

3. **用户体验改进**：
   - 优化表单验证，提供即时反馈
   - 添加更多的动画效果，提升页面活力
   - 改进错误提示，提供更清晰的操作指导

## 8. Bibliography

1. Flask 官方文档：https://flask.palletsprojects.com/
2. SQLAlchemy 官方文档：https://www.sqlalchemy.org/
3. WCAG 2.1 可访问性指南：https://www.w3.org/TR/WCAG21/
4. VRChat 开发者文档：https://docs.vrchat.com/