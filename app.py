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
# 错误处理和事务管理
# ------------------------------

def handle_db_operation(operation_func, success_redirect=None,
                        success_message=None, error_template=None,
                        success_redirect_args=None, **kwargs):
    """统一的数据库操作错误处理函数

    Args:
        operation_func: 执行数据库操作的函数
        success_redirect: 成功后的重定向路由
        success_message: 成功后的Flash消息
        error_template: 错误时渲染的模板
        success_redirect_args: 重定向的额外参数（字典）
        **kwargs: 传递给operation_func的参数

    Returns:
        Flask响应对象
    """
    from flask import flash, redirect, url_for, render_template

    try:
        # 执行数据库操作
        result = operation_func(**kwargs)

        # 提交事务
        db.session.commit()

        # 设置成功消息
        if success_message:
            flash(success_message, 'success')

        # 重定向或返回结果
        if success_redirect:
            if success_redirect_args:
                return redirect(
                    url_for(success_redirect, **success_redirect_args))
            return redirect(url_for(success_redirect))
        return result

    except Exception as e:
        # 回滚事务
        db.session.rollback()

        # 记录错误（实际项目中应使用日志库）
        print(f"数据库操作错误: {str(e)}")

        # 设置错误消息
        error_msg = f"操作失败: {str(e)}"
        flash(error_msg, 'danger')

        # 返回错误页面或重定向
        if error_template:
            return render_template(error_template, error=error_msg, **kwargs)
        # 默认重定向到上一页或主页
        return redirect(url_for('index'))


def validate_event_form(form_data):
    """验证事件表单数据

    Args:
        form_data: 表单数据字典

    Returns:
        tuple: (是否有效, 错误消息列表, 清理后的数据)
    """
    errors = []
    cleaned_data = {}

    # 必填字段验证
    required_fields = ['friend_name', 'world_name', 'start_time', 'end_time']
    for field in required_fields:
        value = form_data.get(field, '').strip()
        if not value:
            errors.append(f"'{field}' 是必填字段")
        cleaned_data[field] = value

    # 时间格式验证
    if 'start_time' in cleaned_data and 'end_time' in cleaned_data:
        try:
            start_time = datetime.strptime(
                cleaned_data['start_time'], '%Y-%m-%dT%H:%M')
            end_time = datetime.strptime(
                cleaned_data['end_time'], '%Y-%m-%dT%H:%M')

            if end_time <= start_time:
                errors.append("结束时间必须晚于开始时间")
        except ValueError:
            errors.append("时间格式不正确，请使用 YYYY-MM-DDTHH:MM 格式")

    # 清理输入，防止XSS攻击
    for key, value in cleaned_data.items():
        if isinstance(value, str):
            # 简单的HTML标签过滤
            cleaned_data[key] = value.replace('<', '&lt;').replace('>', '&gt;')

    return len(errors) == 0, errors, cleaned_data


def handle_api_db_operation(
        operation_func, success_response_func=None, **kwargs):
    """统一的API数据库操作错误处理函数

    Args:
        operation_func: 执行数据库操作的函数
        success_response_func: 成功时创建响应的函数
        **kwargs: 传递给operation_func的参数

    Returns:
        Flask JSON响应对象
    """
    from flask import jsonify

    try:
        # 执行数据库操作
        result = operation_func(**kwargs)

        # 提交事务
        db.session.commit()

        # 创建成功响应
        if success_response_func:
            return success_response_func(result)
        return jsonify({'success': True, 'result': result})

    except Exception as e:
        # 回滚事务
        db.session.rollback()

        # 记录错误
        print(f"API数据库操作错误: {str(e)}")

        # 返回错误响应
        return jsonify({'success': False, 'error': str(e)}), 500


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

    # 使用API错误处理包装的数据库操作
    def like_event_operation():
        event.likes += 1  # 增加点赞数
        return event.likes

    # 成功响应函数
    def success_response(likes):
        return jsonify({'success': True, 'likes': likes})

    # 调用API错误处理函数
    return handle_api_db_operation(
        operation_func=like_event_operation,
        success_response_func=success_response
    )


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
        # 表单验证
        is_valid, errors, cleaned_data = validate_event_form(request.form)

        if not is_valid:
            # 返回表单并显示错误
            for error in errors:
                flash(error, 'danger')
            return render_template('create_event.html',
                                   friend_name=request.form.get('friend_name'),
                                   world_name=request.form.get('world_name'),
                                   world_tags=request.form.get('world_tags'),
                                   start_time=request.form.get('start_time'),
                                   end_time=request.form.get('end_time'),
                                   notes=request.form.get('notes'))

        # 使用错误处理包装的数据库操作
        def create_event_operation(
                friend_name, world_name, world_tags, start_time_str, end_time_str, notes):
            # 处理时间
            start_time, end_time, duration = process_event_time(
                start_time_str, end_time_str)

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
            db.session.add(new_event)
            return new_event

        # 调用错误处理函数
        return handle_db_operation(
            operation_func=create_event_operation,
            success_redirect='index',
            success_message='事件创建成功！',
            error_template='create_event.html',
            friend_name=cleaned_data['friend_name'],
            world_name=cleaned_data['world_name'],
            world_tags=request.form.get('world_tags', ''),
            start_time_str=cleaned_data['start_time'],
            end_time_str=cleaned_data['end_time'],
            notes=request.form.get('notes', '')
        )

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
        # 表单验证
        is_valid, errors, cleaned_data = validate_event_form(request.form)

        if not is_valid:
            # 返回表单并显示错误
            for error in errors:
                flash(error, 'danger')
            # 重新格式化时间用于表单
            event.start_time_formatted = request.form.get('start_time', '')
            event.end_time_formatted = request.form.get('end_time', '')
            return render_template('edit_event.html', event=event,
                                   friend_name=request.form.get('friend_name'),
                                   world_name=request.form.get('world_name'),
                                   world_tags=request.form.get('world_tags'),
                                   notes=request.form.get('notes'))

        # 使用错误处理包装的数据库操作
        def edit_event_operation(
                friend_name, world_name, world_tags, start_time_str, end_time_str, notes):
            # 处理时间
            start_time, end_time, duration = process_event_time(
                start_time_str, end_time_str)

            # 查找或创建世界
            world = get_or_create_world(world_name, world_tags)

            # 更新事件
            event.friend_name = friend_name
            event.world_id = world.id
            event.start_time = start_time
            event.end_time = end_time
            event.duration = duration
            event.notes = notes

            return event

        # 调用错误处理函数
        return handle_db_operation(
            operation_func=edit_event_operation,
            success_redirect='event_detail',
            success_message='事件更新成功！',
            error_template='edit_event.html',
            success_redirect_args={'event_id': event.id},
            friend_name=cleaned_data['friend_name'],
            world_name=cleaned_data['world_name'],
            world_tags=request.form.get('world_tags', ''),
            start_time_str=cleaned_data['start_time'],
            end_time_str=cleaned_data['end_time'],
            notes=request.form.get('notes', '')
        )

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

    # 使用错误处理包装的数据库操作
    def delete_event_operation():
        db.session.delete(event)

    # 调用错误处理函数
    return handle_db_operation(
        operation_func=delete_event_operation,
        success_redirect='index',
        success_message='事件删除成功！'
    )


# ------------------------------
# 标签管理路由
# ------------------------------

@app.route('/event/<int:event_id>/tags', methods=['POST'])
@login_required
def add_tag(event_id):
    """为事件添加标签"""
    # 获取事件，不存在则返回404
    event = SharedEvent.query.get_or_404(event_id)

    # 验证事件所有者
    if event.user_id != current_user.id:
        return redirect(url_for('index'))

    # 获取标签名称
    tag_name = request.form.get('tag_name', '').strip()

    # 验证标签名称
    if not tag_name:
        flash('标签名称不能为空', 'danger')
        return redirect(url_for('event_detail', event_id=event_id))

    if len(tag_name) > 50:
        flash('标签名称不能超过50个字符', 'danger')
        return redirect(url_for('event_detail', event_id=event_id))

    # 使用错误处理包装的数据库操作
    def add_tag_operation():
        # 检查标签是否已存在
        existing_tag = EventTag.query.filter_by(
            event_id=event_id, tag_name=tag_name).first()
        if existing_tag:
            # 如果标签已存在，不视为错误，只是不重复添加
            return '标签已存在'

        # 添加新标签
        new_tag = EventTag(event_id=event.id, tag_name=tag_name)
        db.session.add(new_tag)
        return '标签添加成功'

    # 调用错误处理函数
    return handle_db_operation(
        operation_func=add_tag_operation,
        success_redirect='event_detail',
        success_message='标签添加成功！',
        success_redirect_args={'event_id': event_id}
    )


# ------------------------------
# 备注管理路由
# ------------------------------

@app.route('/event/<int:event_id>/notes', methods=['POST'])
@login_required
def update_notes(event_id):
    """更新事件备注"""
    event = SharedEvent.query.get_or_404(event_id)

    # 验证事件所有者
    if event.user_id != current_user.id:
        return redirect(url_for('index'))

    # 获取备注并清理输入
    notes = request.form.get('notes', '')
    # 简单的HTML标签过滤
    cleaned_notes = notes.replace('<', '&lt;').replace('>', '&gt;')

    # 使用错误处理包装的数据库操作
    def update_notes_operation():
        event.notes = cleaned_notes
        return '备注更新成功'

    # 调用错误处理函数
    return handle_db_operation(
        operation_func=update_notes_operation,
        success_redirect='event_detail',
        success_message='备注更新成功！',
        success_redirect_args={'event_id': event_id}
    )


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
