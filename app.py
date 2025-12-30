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


class GameLog(db.Model):
    """真实游戏日志模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)  # 事件发生时间
    event_type = db.Column(
        db.String(50),
        nullable=False)  # 事件类型：位置变动、玩家加入、玩家离开
    world_name = db.Column(db.String(200))  # 世界名称
    world_id = db.Column(db.String(100))  # 世界ID，如#53949
    player_name = db.Column(db.String(80), nullable=False)  # 玩家名称
    is_friend = db.Column(db.Boolean, default=False)  # 是否为好友
    created_at = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间


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


def preprocess_query(query):
    """查询预处理层

    Args:
        query: 原始查询字符串

    Returns:
        tuple: (预处理后的查询, 提取的日期关键词)
    """
    import re

    # 1. 规范化处理
    query = query.strip().lower()

    # 2. 中文数字转阿拉伯数字
    # 简单实现，支持年份转换
    chinese_nums = {
        '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
        '五': '5', '六': '6', '七': '7', '八': '8', '九': '9'
    }

    def replace_chinese_num(match):
        num_str = match.group(0)
        result = ''
        for char in num_str:
            if char in chinese_nums:
                result += chinese_nums[char]
            else:
                result += char
        return result

    # 替换中文数字，特别是年份
    query = re.sub(r'[零一二三四五六七八九]{4}', replace_chinese_num, query)

    # 3. 提取日期相关词汇
    date_keywords = []
    # 简单的日期关键词提取
    date_patterns = [
        r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
        r'\d{4}-\d{1,2}',           # YYYY-MM
        r'\d{1,2}-\d{1,2}',         # MM-DD
        r'\d{4}年\d{1,2}月\d{1,2}日?',  # YYYY年MM月DD日
        r'\d{1,2}月\d{1,2}日?',       # MM月DD日
        r'今天|昨天|明天|前天|后天|大前天|大后天',
        r'\d+天前|\d+天后',
        r'春节|国庆节|元旦|劳动节|中秋节'
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, query)
        date_keywords.extend(matches)

    return query, date_keywords


def parse_relative_date(query, base_date=None):
    """相对日期解析

    Args:
        query: 查询字符串
        base_date: 基准日期，默认为当前日期

    Returns:
        datetime: 解析后的日期
    """
    import re
    from datetime import datetime, timedelta

    if base_date is None:
        base_date = datetime.now()

    patterns = {
        r'^(今天|today)$': 0,
        r'^(昨天|yesterday)$': -1,
        r'^(明天|tomorrow)$': 1,
        r'^前天$': -2,
        r'^后天$': 2,
        r'^大前天$': -3,
        r'^大后天$': 3,
        r'^(\d+)天前$': lambda m: -int(m.group(1)),
        r'^(\d+)天后$': lambda m: int(m.group(1))
    }

    for pattern, delta in patterns.items():
        if match := re.fullmatch(pattern, query):
            if callable(delta):
                offset = delta(match)
            else:
                offset = delta
            # 创建一个新的日期对象，只保留年、月、日，不保留时间
            result_date = base_date + timedelta(days=offset)
            return result_date.replace(
                hour=0, minute=0, second=0, microsecond=0)

    return None


def parse_chinese_date(text, base_date=None):
    """中文日期识别

    Args:
        text: 中文日期文本
        base_date: 基准日期，默认为当前日期

    Returns:
        datetime: 解析后的日期
    """
    import re
    from datetime import datetime, timedelta

    if base_date is None:
        base_date = datetime.now()

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

    # 中文日期映射
    chinese_day_map = {
        '初一': 1, '初二': 2, '初三': 3, '初四': 4, '初五': 5,
        '初六': 6, '初七': 7, '初八': 8, '初九': 9, '初十': 10,
        '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
        '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        '二十一': 21, '二十二': 22, '二十三': 23, '二十四': 24, '二十五': 25,
        '二十六': 26, '二十七': 27, '二十八': 28, '二十九': 29, '三十': 30, '三十一': 31
    }

    # 辅助函数：将中文数字转换为阿拉伯数字
    def chinese_to_arabic(chinese_num):
        if chinese_num in chinese_month_map:
            return chinese_month_map[chinese_num]
        if chinese_num in chinese_day_map:
            return chinese_day_map[chinese_num]

        # 处理复杂的中文数字，如"二十五"
        if len(chinese_num) == 1:
            return chinese_num_map.get(chinese_num, None)
        elif len(chinese_num) == 2:
            if chinese_num[0] == '十':
                return 10 + chinese_num_map.get(chinese_num[1], 0)
            else:
                return chinese_num_map.get(
                    chinese_num[0], 0) * 10 + chinese_num_map.get(chinese_num[1], 0)
        elif len(chinese_num) == 3:
            return 20 + chinese_num_map.get(chinese_num[2], 0)  # 如"二十一"=21
        return None

    # 模式1: YYYY年MM月DD日
    pattern1 = r'(\d{4})年(\d{1,2})月(\d{1,2})日?'
    match = re.match(pattern1, text)
    if match:
        year, month, day = match.groups()
        return datetime(int(year), int(month), int(day))

    # 模式2: MM月DD日
    pattern2 = r'(\d{1,2})月(\d{1,2})日?'
    match = re.match(pattern2, text)
    if match:
        month, day = match.groups()
        return datetime(base_date.year, int(month), int(day))

    # 模式3: 中文月份 + 中文日期（如"十二月二十五日"）
    pattern3 = r'([\u4e00-\u9fa5]+月)([\u4e00-\u9fa5]+日?)'
    match = re.match(pattern3, text)
    if match:
        month_str, day_str = match.groups()
        month_str = month_str.rstrip('月')
        day_str = day_str.rstrip('日')

        # 处理月份
        month = chinese_month_map.get(month_str, None)
        if month is None:
            return None

        # 处理日期
        day = chinese_to_arabic(day_str)
        if day is None:
            day = chinese_day_map.get(day_str, None)
        if day is None:
            return None

        return datetime(base_date.year, month, day)

    # 模式4: 中文月份 + 数字日期（如"十二月25日"）
    pattern4 = r'([\u4e00-\u9fa5]+月)(\d{1,2})日?'
    match = re.match(pattern4, text)
    if match:
        month_str, day_str = match.groups()
        month_str = month_str.rstrip('月')

        # 处理月份
        month = chinese_month_map.get(month_str, None)
        if month is None:
            return None

        # 处理日期
        day = int(day_str)

        return datetime(base_date.year, month, day)

    return None


def parse_holiday(text, base_year=None):
    """节假日识别

    Args:
        text: 节假日文本
        base_year: 基准年份，默认为当前年份

    Returns:
        datetime: 节假日的具体日期
    """
    from datetime import datetime

    if base_year is None:
        base_year = datetime.now().year

    holidays = {
        "元旦": f"{base_year}-01-01",
        "春节": f"{base_year}-02-10",  # 2025年春节是2月10日，实际应用中需要更复杂的计算
        "劳动节": f"{base_year}-05-01",
        "国庆节": f"{base_year}-10-01",
        "中秋节": f"{base_year}-09-12"   # 2025年中秋节是9月12日
    }

    for holiday, date_str in holidays.items():
        if holiday in text:
            return datetime.strptime(date_str, '%Y-%m-%d')

    return None


def parse_search_query(search_query):
    """解析搜索查询，提取关键词和日期范围
    采用多模式解析器架构，支持多种日期格式

    Args:
        search_query: 搜索查询字符串

    Returns:
        tuple: (关键词列表, 开始日期, 结束日期)
    """
    import re
    from datetime import datetime, timedelta

    keywords = []
    start_date = None
    end_date = None

    if not search_query:
        return keywords, start_date, end_date

    # 预处理查询
    processed_query, date_keywords = preprocess_query(search_query)

    # 分割搜索词
    search_terms = processed_query.split()

    # 日期格式正则表达式
    date_patterns = [
        (r'^(\d{4}-\d{1,2}-\d{1,2})$', '%Y-%m-%d'),  # YYYY-MM-DD
        (r'^(\d{4}-\d{1,2})$', '%Y-%m'),           # YYYY-MM
    ]

    # 逐个处理搜索词
    for term in search_terms:
        is_date = False

        # 尝试解析相对日期
        rel_date = parse_relative_date(term)
        if rel_date:
            is_date = True
            # 对于相对日期，开始和结束日期都设为该日期
            if not start_date or rel_date < start_date:
                start_date = rel_date
            if not end_date or rel_date > end_date:
                end_date = rel_date

        # 尝试解析中文日期
        elif (chinese_date := parse_chinese_date(term)) is not None:
            is_date = True
            if not start_date or chinese_date < start_date:
                start_date = chinese_date
            if not end_date or chinese_date > end_date:
                end_date = chinese_date

        # 尝试解析节假日
        elif (holiday_date := parse_holiday(term)) is not None:
            is_date = True
            if not start_date or holiday_date < start_date:
                start_date = holiday_date
            if not end_date or holiday_date > end_date:
                end_date = holiday_date

        # 尝试解析标准日期格式
        else:
            for pattern, date_format in date_patterns:
                match = re.match(pattern, term)
                if match:
                    is_date = True
                    try:
                        date_obj = datetime.strptime(
                            match.group(1), date_format)

                        if date_format == '%Y-%m-%d':
                            # 具体日期，设置为当天
                            if not start_date or date_obj < start_date:
                                start_date = date_obj
                            if not end_date or date_obj > end_date:
                                end_date = date_obj
                        elif date_format == '%Y-%m':
                            # 月份，设置为该月的第一天和最后一天
                            month_start = date_obj
                            # 计算该月的最后一天
                            if month_start.month == 12:
                                month_end = month_start.replace(
                                    year=month_start.year + 1, month=1, day=1) - timedelta(days=1)
                            else:
                                month_end = month_start.replace(
                                    month=month_start.month + 1, day=1) - timedelta(days=1)

                            if not start_date or month_start < start_date:
                                start_date = month_start
                            if not end_date or month_end > end_date:
                                end_date = month_end
                    except ValueError:
                        pass
                    break

        # 如果不是日期，添加到关键词列表
        if not is_date:
            keywords.append(term)

    return keywords, start_date, end_date


def enhance_search_conditions(keywords):
    """增强搜索条件，支持更高级的模糊匹配

    Args:
        keywords: 关键词列表

    Returns:
        list: 搜索条件列表
    """
    from sqlalchemy import or_, and_

    search_conditions = []

    for keyword in keywords:
        keyword_like = f'%{keyword}%'

        # 基本搜索条件
        conditions = [
            SharedEvent.friend_name.ilike(keyword_like),
            World.world_name.ilike(keyword_like),
            World.tags.ilike(keyword_like),
            EventTag.tag_name.ilike(keyword_like)
        ]

        # 高级模糊匹配：支持多种模糊匹配策略
        if len(keyword) > 1:
            # 前缀匹配
            conditions.append(SharedEvent.friend_name.ilike(f'{keyword}%'))
            conditions.append(World.world_name.ilike(f'{keyword}%'))

            # 后缀匹配
            conditions.append(SharedEvent.friend_name.ilike(f'%{keyword}'))
            conditions.append(World.world_name.ilike(f'%{keyword}'))

        if len(keyword) > 2:
            # 子串匹配
            conditions.append(
                SharedEvent.friend_name.ilike(f'%{keyword[:2]}%'))
            conditions.append(World.world_name.ilike(f'%{keyword[:2]}%'))

            # 对于长度大于3的关键词，使用多个子串匹配
            if len(keyword) > 3:
                # 取前3个字符和后3个字符
                conditions.append(
                    SharedEvent.friend_name.ilike(f'%{keyword[:3]}%'))
                conditions.append(World.world_name.ilike(f'%{keyword[:3]}%'))
                conditions.append(
                    SharedEvent.friend_name.ilike(f'%{keyword[-3:]}%'))
                conditions.append(World.world_name.ilike(f'%{keyword[-3:]}%'))

        search_conditions.append(or_(*conditions))

    return search_conditions


@app.route('/')
@login_required
def index():
    """时间线主页，支持标签筛选和高级搜索"""
    # 收集所有可用标签
    all_unique_tags = get_all_unique_tags()

    # 处理标签筛选
    selected_tag = request.args.get('tag')
    query = SharedEvent.query.filter_by(user_id=current_user.id)
    filtered_query = filter_events_by_tag(query, selected_tag)

    # 处理搜索
    search_query = request.args.get('search')
    start_date = None
    end_date = None

    if search_query:
        from sqlalchemy import or_, and_

        # 解析搜索查询，提取关键词和日期
        keywords, parsed_start_date, parsed_end_date = parse_search_query(
            search_query)
        start_date = parsed_start_date
        end_date = parsed_end_date

        # 构建搜索条件
        search_conditions = []

        if keywords:
            # 增强搜索条件，支持更高级的模糊匹配
            keyword_conditions = enhance_search_conditions(keywords)
            search_conditions.extend(keyword_conditions)

        if search_conditions:
            # 连接表并应用搜索条件
            filtered_query = filtered_query.join(World)
            filtered_query = filtered_query.outerjoin(EventTag)
            # 使用OR组合关键词条件，更符合用户搜索习惯
            filtered_query = filtered_query.filter(or_(*search_conditions))
            filtered_query = filtered_query.group_by(SharedEvent.id)  # 去重

    # 处理日期范围
    if start_date:
        from datetime import datetime
        filtered_query = filtered_query.filter(
            SharedEvent.start_time >= start_date)

    if end_date:
        from datetime import timedelta
        # 包含结束日期当天
        end_datetime = end_date + timedelta(days=1)
        filtered_query = filtered_query.filter(
            SharedEvent.start_time < end_datetime)

    # 按时间倒序获取事件
    events = filtered_query.order_by(SharedEvent.start_time.desc()).all()

    return render_template(
        'index.html',
        events=events,
        all_tags=all_unique_tags,
        selected_tag=selected_tag,
        search_query=search_query
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
# 游戏日志导入和转换路由
# ------------------------------

@app.route('/api/gamelog/import', methods=['POST'])
@login_required
def import_game_logs():
    """导入真实游戏日志数据"""
    # 从请求中获取日志数据
    logs_data = request.get_json()
    if not logs_data:
        return jsonify({'success': False, 'error': '没有提供日志数据'}), 400

    # 使用API错误处理包装的数据库操作
    def import_logs_operation():
        imported_count = 0
        for log_entry in logs_data:
            # 解析日志条目
            timestamp_str = log_entry.get('timestamp')
            event_type = log_entry.get('event_type')
            world_name = log_entry.get('world_name')
            world_id = log_entry.get('world_id')
            player_name = log_entry.get('player_name')
            is_friend = log_entry.get('is_friend', False)

            # 验证必填字段
            if not all([timestamp_str, event_type, player_name]):
                continue

            # 转换时间字符串为datetime对象
            try:
                # 处理不同的时间格式
                if ' ' in timestamp_str and '/' in timestamp_str:
                    # 格式：12/28 01:53
                    timestamp = datetime.strptime(timestamp_str, '%m/%d %H:%M')
                    # 设置当前年份
                    timestamp = timestamp.replace(year=datetime.now().year)
                else:
                    # ISO格式或其他格式
                    timestamp = datetime.fromisoformat(timestamp_str)
            except ValueError:
                continue

            # 创建游戏日志记录
            game_log = GameLog(
                user_id=current_user.id,
                timestamp=timestamp,
                event_type=event_type,
                world_name=world_name,
                world_id=world_id,
                player_name=player_name,
                is_friend=is_friend
            )
            db.session.add(game_log)
            imported_count += 1

        return imported_count

    # 成功响应函数
    def success_response(imported_count):
        return jsonify({'success': True, 'imported_count': imported_count})

    # 调用API错误处理函数
    return handle_api_db_operation(
        operation_func=import_logs_operation,
        success_response_func=success_response
    )


@app.route('/api/gamelog/convert', methods=['POST'])
@login_required
def convert_game_logs():
    """将游戏日志转换为SharedEvent"""
    # 使用API错误处理包装的数据库操作
    def convert_logs_operation():
        # 1. 获取当前用户的所有游戏日志
        game_logs = GameLog.query.filter_by(
            user_id=current_user.id).order_by(
            GameLog.timestamp).all()

        # 2. 按玩家分组，跟踪玩家的加入和离开事件
        player_sessions = {}
        converted_count = 0

        for log in game_logs:
            player_name = log.player_name

            if log.event_type == '玩家加入':
                # 记录玩家加入时间和当前世界
                player_sessions[player_name] = {
                    'start_time': log.timestamp,
                    'world_name': log.world_name,
                    'world_id': log.world_id
                }

            elif log.event_type == '玩家离开' and player_name in player_sessions:
                # 玩家离开，创建SharedEvent
                session = player_sessions.pop(player_name)

                # 计算持续时间
                duration = int(
                    (log.timestamp - session['start_time']).total_seconds())

                # 查找或创建世界
                world = get_or_create_world(session['world_name'], '')

                # 创建SharedEvent
                event = SharedEvent(
                    user_id=current_user.id,
                    world_id=world.id,
                    friend_name=player_name,
                    start_time=session['start_time'],
                    end_time=log.timestamp,
                    duration=duration
                )
                db.session.add(event)
                converted_count += 1

        return converted_count

    # 成功响应函数
    def success_response(converted_count):
        return jsonify({'success': True, 'converted_count': converted_count})

    # 调用API错误处理函数
    return handle_api_db_operation(
        operation_func=convert_logs_operation,
        success_response_func=success_response
    )


@app.route('/api/gamelog/bulk_import', methods=['POST'])
@login_required
def bulk_import_game_logs():
    """批量导入游戏日志文本数据"""
    """批量导入游戏日志文本数据，格式如：
    12/28 01:53 位置变动 メゾン荘 201号室 #53949 friends+
    12/28 01:52 玩家离开 💚 SaKi43
    """
    log_text = request.form.get('log_text', '')
    if not log_text:
        return jsonify({'success': False, 'error': '没有提供日志文本'}), 400

    # 使用API错误处理包装的数据库操作
    def bulk_import_operation():
        # 预处理：将多行记录合并为单行
        processed_lines = []
        current_line = []

        for line in log_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue

            # 检查是否是新记录的开始（以日期格式开头，如 12/28）
            if '/' in line and len(line.split()[0]) >= 5:
                # 保存当前记录（如果有）
                if current_line:
                    processed_lines.append(' '.join(current_line))
                # 开始新记录
                current_line = [line]
            else:
                # 追加到当前记录
                if current_line:
                    current_line.append(line)

        # 保存最后一条记录
        if current_line:
            processed_lines.append(' '.join(current_line))

        imported_count = 0

        for full_line in processed_lines:
            full_line = full_line.strip()
            if not full_line:
                continue

            # 解析日志行
            parts = full_line.split()
            if len(parts) < 4:
                continue

            # 解析时间
            date_part = parts[0]
            time_part = parts[1]
            try:
                timestamp_str = f"{date_part} {time_part}"
                timestamp = datetime.strptime(timestamp_str, '%m/%d %H:%M')
                timestamp = timestamp.replace(year=datetime.now().year)
            except ValueError:
                continue

            # 解析事件类型
            event_type = parts[2]
            if event_type not in ['位置变动', '玩家加入', '玩家离开']:
                continue

            player_name = ''
            world_name = ''
            world_id = ''
            is_friend = False

            if event_type == '位置变动':
                # 解析世界信息
                # 格式：位置变动 メゾン荘 201号室 #53949 friends+
                world_parts = parts[3:]
                for i, part in enumerate(world_parts):
                    if part.startswith('#'):
                        world_id = part
                        world_name = ' '.join(world_parts[:i])
                        if i + \
                                1 < len(world_parts) and world_parts[i + 1] == 'friends+':
                            is_friend = True
                        break
                else:
                    world_name = ' '.join(world_parts)

                player_name = '系统'

            else:  # 玩家加入或玩家离开
                # 解析玩家信息
                # 格式：玩家离开 💚 SaKi43
                player_parts = parts[3:]
                if len(player_parts) >= 2:
                    if player_parts[0] == '💚':
                        is_friend = True
                        player_name = ' '.join(player_parts[1:])
                    else:
                        is_friend = False
                        player_name = ' '.join(player_parts)
                elif len(player_parts) == 1:
                    player_name = player_parts[0]

            # 创建游戏日志记录
            game_log = GameLog(
                user_id=current_user.id,
                timestamp=timestamp,
                event_type=event_type,
                world_name=world_name,
                world_id=world_id,
                player_name=player_name,
                is_friend=is_friend
            )
            db.session.add(game_log)
            imported_count += 1

        return imported_count

    # 成功响应函数
    def success_response(imported_count):
        return jsonify({'success': True, 'imported_count': imported_count})

    # 调用API错误处理函数
    return handle_api_db_operation(
        operation_func=bulk_import_operation,
        success_response_func=success_response
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

def init_db():
    """初始化数据库"""
    with app.app_context():
        """应用上下文内初始化数据库和模拟数据"""
        db.create_all()  # 创建所有数据库表

        # 如果没有数据，生成模拟数据
        if not User.query.first():
            generate_mock_data()


# 确保在应用加载时就初始化数据库，无论运行方式如何
init_db()


# ------------------------------
# 启动应用
# ------------------------------

if __name__ == '__main__':
    app.run(debug=True)  # 开发模式运行应用
