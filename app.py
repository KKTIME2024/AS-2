from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import random
import json


# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vrchat_memories.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# 初始化数据库和登录管理器
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # 设置登录页面


# ------------------------------
# 数据库模型定义
# ------------------------------

class User(UserMixin, db.Model):
    """用户模型"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    events = db.relationship('SharedEvent', backref='user', lazy=True)


class World(db.Model):
    """世界模型"""
    id = db.Column(db.Integer, primary_key=True)
    world_name = db.Column(db.String(200), nullable=False)
    world_id = db.Column(db.String(100), unique=True)
    tags = db.Column(db.Text)  # 以逗号分隔的标签字符串
    events = db.relationship('SharedEvent', backref='world', lazy=True)


class SharedEvent(db.Model):
    """共同房间事件模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    friend_name = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 持续时间（秒）
    notes = db.Column(db.Text, nullable=True)  # 事件备注
    likes = db.Column(db.Integer, default=0)  # 点赞数
    custom_tags = db.relationship(
        'EventTag',
        backref='event',
        lazy=True,  # 懒加载
        cascade='all, delete-orphan'  # 级联删除
    )


class EventTag(db.Model):
    """事件标签关联模型（多对多关系）"""
    event_id = db.Column(
        db.Integer,
        db.ForeignKey('shared_event.id'),
        primary_key=True
    )
    tag_name = db.Column(db.String(50), primary_key=True)


# ------------------------------
# 登录管理器回调
# ------------------------------

@login_manager.user_loader
def load_user(user_id):
    """根据用户ID加载用户对象"""
    return User.query.get(int(user_id))


# ------------------------------
# 路由定义
# ------------------------------

def get_all_unique_tags():
    """获取所有唯一标签，包括世界标签和事件自定义标签"""
    # 从世界中提取标签
    world_tags = set()
    worlds = World.query.all()
    for world in worlds:
        if world.tags:
            for tag in world.tags.split(','):
                world_tags.add(tag.strip())

    # 从事件自定义标签中提取标签
    event_tags = set()
    all_event_tags = EventTag.query.all()
    for tag in all_event_tags:
        event_tags.add(tag.tag_name)

    # 合并所有唯一标签并排序
    return sorted(list(world_tags.union(event_tags)))


def filter_events_by_tag(event_query, selected_tag):
    """根据标签筛选事件"""
    if not selected_tag:
        return event_query

    # 查找包含该标签的世界
    tagged_worlds = World.query.filter(
        World.tags.like(f'%{selected_tag}%')).all()
    tagged_world_ids = [world.id for world in tagged_worlds]

    # 查找包含该自定义标签的事件
    tagged_events = EventTag.query.filter_by(tag_name=selected_tag).all()
    tagged_event_ids = [tag.event_id for tag in tagged_events]

    # 合并结果：世界包含该标签 或 事件有该自定义标签
    return event_query.filter(
        (SharedEvent.world_id.in_(tagged_world_ids)) |
        (SharedEvent.id.in_(tagged_event_ids))
    )


@app.route('/')
@login_required
def index():
    """时间线主页，支持标签筛选"""
    # 收集所有可用标签
    all_unique_tags = get_all_unique_tags()

    # 处理标签筛选
    selected_tag = request.args.get('tag')
    query = SharedEvent.query.filter_by(user_id=current_user.id)
    filtered_query = filter_events_by_tag(query, selected_tag)

    # 按时间倒序获取事件
    events = filtered_query.order_by(SharedEvent.start_time.desc()).all()

    return render_template(
        'index.html',
        events=events,
        all_tags=all_unique_tags,
        selected_tag=selected_tag
    )


@app.route('/event/<int:event_id>')
@login_required
def event_detail(event_id):
    """事件详情页面"""
    event = SharedEvent.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 查找用户
        user = User.query.filter_by(username=username).first()

        # 验证用户和密码
        if user and check_password_hash(user.password_hash, password):
            login_user(user)  # 登录用户
            return redirect(url_for('index'))

        # 登录失败，返回错误信息
        return render_template(
            'login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template(
                'register.html', error='Username already exists')

        # 创建新用户，使用哈希密码
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)

        # 保存到数据库
        db.session.add(new_user)
        db.session.commit()

        # 自动登录新用户
        login_user(new_user)
        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/logout')
def logout():
    """登出功能"""
    logout_user()  # 登出用户
    return redirect(url_for('login'))


# ------------------------------
# AJAX API路由
# ------------------------------

@app.route('/api/event/<int:event_id>/like', methods=['POST'])
@login_required
def like_event(event_id):
    """AJAX点赞功能"""
    event = SharedEvent.query.get_or_404(event_id)
    event.likes += 1  # 增加点赞数
    db.session.commit()
    return jsonify({'likes': event.likes})


# ------------------------------
# 事件管理路由
# ------------------------------

def process_event_time(start_time_str, end_time_str):
    """处理事件时间字符串，返回datetime对象和持续时间"""
    start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
    end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
    duration = int((end_time - start_time).total_seconds())
    return start_time, end_time, duration


def get_or_create_world(world_name, world_tags):
    """查找或创建世界"""
    world = World.query.filter_by(world_name=world_name).first()
    if not world:
        world = World(world_name=world_name, tags=world_tags)
        db.session.add(world)
        db.session.commit()
    return world


@app.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """创建新事件"""
    if request.method == 'POST':
        # 获取表单数据
        friend_name = request.form.get('friend_name')
        world_name = request.form.get('world_name')
        world_tags = request.form.get('world_tags')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        notes = request.form.get('notes')

        # 处理时间
        start_time, end_time, duration = process_event_time(start_time_str, end_time_str)

        # 查找或创建世界
        world = get_or_create_world(world_name, world_tags)

        # 创建新事件
        new_event = SharedEvent(
            user_id=current_user.id,
            world_id=world.id,
            friend_name=friend_name,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            notes=notes
        )

        # 保存到数据库
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create_event.html')


@app.route('/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """编辑事件"""
    # 获取事件，不存在则返回404
    event = SharedEvent.query.get_or_404(event_id)

    # 验证事件所有者
    if event.user_id != current_user.id:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # 获取表单数据
        friend_name = request.form.get('friend_name')
        world_name = request.form.get('world_name')
        world_tags = request.form.get('world_tags')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        notes = request.form.get('notes')

        # 处理时间
        start_time, end_time, duration = process_event_time(start_time_str, end_time_str)

        # 查找或创建世界
        world = get_or_create_world(world_name, world_tags)

        # 更新事件
        event.friend_name = friend_name
        event.world_id = world.id
        event.start_time = start_time
        event.end_time = end_time
        event.duration = duration
        event.notes = notes

        # 保存更改
        db.session.commit()

        return redirect(url_for('event_detail', event_id=event.id))

    # 格式化时间用于表单
    event.start_time_formatted = event.start_time.strftime('%Y-%m-%dT%H:%M')
    event.end_time_formatted = event.end_time.strftime('%Y-%m-%dT%H:%M')

    return render_template('edit_event.html', event=event)


@app.route('/event/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    """删除事件"""
    # 获取事件，不存在则返回404
    event = SharedEvent.query.get_or_404(event_id)

    # 验证事件所有者
    if event.user_id != current_user.id:
        return redirect(url_for('index'))

    # 删除事件（关联的标签会通过级联删除自动清理）
    db.session.delete(event)
    db.session.commit()

    return redirect(url_for('index'))


# ------------------------------
# 标签管理路由
# ------------------------------

@app.route('/event/<int:event_id>/tags', methods=['POST'])
@login_required
def add_tag(event_id):
    """为事件添加标签"""
    tag_name = request.form.get('tag_name').strip()
    if tag_name:
        event = SharedEvent.query.get_or_404(event_id)

        # 检查标签是否已存在
        existing_tag = EventTag.query.filter_by(
            event_id=event.id,
            tag_name=tag_name
        ).first()

        if not existing_tag:
            # 添加新标签
            new_tag = EventTag(event_id=event.id, tag_name=tag_name)
            db.session.add(new_tag)
            db.session.commit()

    return redirect(url_for('event_detail', event_id=event_id))


# ------------------------------
# 备注管理路由
# ------------------------------

@app.route('/event/<int:event_id>/notes', methods=['POST'])
@login_required
def update_notes(event_id):
    """更新事件备注"""
    notes = request.form.get('notes')
    event = SharedEvent.query.get_or_404(event_id)

    # 更新备注
    event.notes = notes
    db.session.commit()

    return redirect(url_for('event_detail', event_id=event_id))


# ------------------------------
# 模拟数据生成
# ------------------------------

def generate_mock_data():
    """生成模拟数据用于演示"""
    # 创建示例世界
    worlds = [
        World(world_name="The Black Cat", tags="Social,Music,Dance"),
        World(world_name="Murder 4", tags="Game,Horror"),
        World(world_name="Treehouse in the Shade", tags="Social,Relaxing"),
        World(world_name="Just B Club", tags="Music,Dance"),
        World(world_name="Among Us VR", tags="Game,Social")
    ]

    # 保存世界数据
    for world in worlds:
        db.session.add(world)
    db.session.commit()

    # 创建演示用户
    demo_user = User(
        username="demo",
        password_hash=generate_password_hash("demo")  # 使用安全哈希
    )
    db.session.add(demo_user)
    db.session.commit()

    # 示例好友列表
    friends = ["Alice", "Bob", "Charlie", "Diana"]

    # 生成10个示例事件
    for _ in range(10):
        # 随机生成事件时间
        start_time = datetime.now() - timedelta(days=random.randint(0, 30))
        duration = random.randint(300, 7200)  # 5分钟到2小时
        end_time = start_time + timedelta(seconds=duration)

        # 创建事件
        event = SharedEvent(
            user_id=demo_user.id,
            world_id=random.choice(worlds).id,
            friend_name=random.choice(friends),
            start_time=start_time,
            end_time=end_time,
            duration=duration
        )
        db.session.add(event)
    db.session.commit()


# ------------------------------
# 应用初始化
# ------------------------------

with app.app_context():
    """应用上下文内初始化数据库和模拟数据"""
    db.create_all()  # 创建所有数据库表

    # 如果没有数据，生成模拟数据
    if not User.query.first():
        generate_mock_data()


# ------------------------------
# 启动应用
# ------------------------------

if __name__ == '__main__':
    app.run(debug=True)  # 开发模式运行应用
