from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
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
login_manager.login_view = 'login'

# 数据库模型

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    events = db.relationship('SharedEvent', backref='user', lazy=True)

class World(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    world_name = db.Column(db.String(200), nullable=False)
    world_id = db.Column(db.String(100), unique=True)
    tags = db.Column(db.Text)
    events = db.relationship('SharedEvent', backref='world', lazy=True)

class SharedEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'), nullable=False)
    friend_name = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 秒
    notes = db.Column(db.Text)
    likes = db.Column(db.Integer, default=0)
    custom_tags = db.relationship(
        'EventTag',
        backref='event',
        lazy=True)

class EventTag(db.Model):
    event_id = db.Column(db.Integer, db.ForeignKey('shared_event.id'), primary_key=True)
    tag_name = db.Column(db.String(50), primary_key=True)

# 登录管理器回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 路由定义

@app.route('/')
@login_required
def index():
    """时间线主页"""
    events = SharedEvent.query.filter_by(user_id=current_user.id).order_by(SharedEvent.start_time.desc()).all()
    return render_template('index.html', events=events)

@app.route('/event/<int:event_id>')
@login_required
def event_detail(event_id):
    """事件详情页"""
    event = SharedEvent.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password_hash == password:  # 简单密码验证，生产环境应使用哈希
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 简单验证，生产环境应添加更多验证
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')
        new_user = User(username=username, password_hash=password)  # 简单密码存储，生产环境应使用哈希
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    """登出功能"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/event/<int:event_id>/like', methods=['POST'])
@login_required
def like_event(event_id):
    """AJAX点赞功能"""
    event = SharedEvent.query.get_or_404(event_id)
    event.likes = event.likes + 1 if event.likes else 1
    db.session.commit()
    return jsonify({'likes': event.likes})

@app.route('/event/<int:event_id>/tags', methods=['POST'])
@login_required
def add_tag(event_id):
    """添加标签功能"""
    tag_name = request.form.get('tag_name')
    if tag_name:
        event = SharedEvent.query.get_or_404(event_id)
        # 检查标签是否已存在
        existing_tag = EventTag.query.filter_by(event_id=event.id, tag_name=tag_name).first()
        if not existing_tag:
            new_tag = EventTag(event_id=event.id, tag_name=tag_name)
            db.session.add(new_tag)
            db.session.commit()
    return redirect(url_for('event_detail', event_id=event_id))

# 辅助函数
def generate_mock_data():
    """生成模拟数据"""
    worlds = [
        World(world_name="The Black Cat", tags="Social,Music,Dance"),
        World(world_name="Murder 4", tags="Game,Horror"),
        World(world_name="Treehouse in the Shade", tags="Social,Relaxing"),
        World(world_name="Just B Club", tags="Music,Dance"),
        World(world_name="Among Us VR", tags="Game,Social")
    ]
    
    friends = ["Alice", "Bob", "Charlie", "Diana"]
    
    for world in worlds:
        db.session.add(world)
    db.session.commit()
    
    # 创建演示用户
    demo_user = User(username="demo", password_hash="demo")
    db.session.add(demo_user)
    db.session.commit()
    
    # 生成10个事件
    for _ in range(10):
        start_time = datetime.now() - timedelta(days=random.randint(0, 30))
        duration = random.randint(300, 7200)  # 5分钟到2小时
        end_time = start_time + timedelta(seconds=duration)
        
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

# 初始化数据库和模拟数据
with app.app_context():
    db.create_all()
    # 如果没有数据，生成模拟数据
    if not User.query.first():
        generate_mock_data()

if __name__ == '__main__':
    app.run(debug=True)
