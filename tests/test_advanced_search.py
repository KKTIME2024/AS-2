import pytest
from datetime import datetime, timedelta
from app import app, db, User, World, SharedEvent, EventTag
from app import preprocess_query, parse_relative_date, parse_chinese_date, parse_holiday


@pytest.fixture
def client():
    """创建一个测试客户端"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

    with app.test_client() as client:
        yield client

    with app.app_context():
        db.drop_all()


@pytest.fixture
def authenticated_client(client):
    """创建一个已认证的测试客户端"""
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # 创建测试用户
        test_user = User(username="testuser", password_hash=generate_password_hash("testpass"))
        db.session.add(test_user)
        db.session.commit()
        
        # 创建测试世界
        world1 = World(world_name="Test World", tags="Social,Music,Dance")
        db.session.add(world1)
        db.session.commit()
        
        # 创建测试事件
        now = datetime.now()
        event1 = SharedEvent(
            user_id=test_user.id,
            world_id=world1.id,
            friend_name="Alice",
            start_time=now - timedelta(days=1),
            end_time=now - timedelta(days=1, hours=1),
            duration=3600
        )
        event2 = SharedEvent(
            user_id=test_user.id,
            world_id=world1.id,
            friend_name="Bob",
            start_time=now,
            end_time=now + timedelta(hours=2),
            duration=7200
        )
        event3 = SharedEvent(
            user_id=test_user.id,
            world_id=world1.id,
            friend_name="Charlie",
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=3),
            duration=10800
        )
        db.session.add_all([event1, event2, event3])
        db.session.commit()

    # 登录用户
    client.post(
        '/login',
        data={'username': 'testuser', 'password': 'testpass'},
        follow_redirects=True
    )
    return client


def test_preprocess_query():
    """测试查询预处理"""
    # 测试基本预处理
    query = "  Test Query 123  "
    processed, date_keywords = preprocess_query(query)
    assert processed == "test query 123"
    
    # 测试中文数字转换
    query = "二零二五年的事件"
    processed, date_keywords = preprocess_query(query)
    assert "2025年" in processed
    
    # 测试日期关键词提取
    query = "2023-12-25 圣诞节 昨天 今天 明天"
    processed, date_keywords = preprocess_query(query)
    assert len(date_keywords) >= 5


def test_parse_relative_date():
    """测试相对日期解析"""
    base_date = datetime(2023, 12, 25)
    
    # 测试今天
    assert parse_relative_date("今天", base_date) == base_date
    
    # 测试昨天
    assert parse_relative_date("昨天", base_date) == base_date - timedelta(days=1)
    
    # 测试明天
    assert parse_relative_date("明天", base_date) == base_date + timedelta(days=1)
    
    # 测试前天
    assert parse_relative_date("前天", base_date) == base_date - timedelta(days=2)
    
    # 测试后天
    assert parse_relative_date("后天", base_date) == base_date + timedelta(days=2)
    
    # 测试大前天
    assert parse_relative_date("大前天", base_date) == base_date - timedelta(days=3)
    
    # 测试大后天
    assert parse_relative_date("大后天", base_date) == base_date + timedelta(days=3)
    
    # 测试N天前
    assert parse_relative_date("5天前", base_date) == base_date - timedelta(days=5)
    
    # 测试N天后
    assert parse_relative_date("5天后", base_date) == base_date + timedelta(days=5)
    
    # 测试英文
    assert parse_relative_date("today", base_date) == base_date
    assert parse_relative_date("yesterday", base_date) == base_date - timedelta(days=1)
    assert parse_relative_date("tomorrow", base_date) == base_date + timedelta(days=1)


def test_parse_chinese_date():
    """测试中文日期识别"""
    base_date = datetime(2023, 12, 25)
    
    # 测试YYYY年MM月DD日格式
    assert parse_chinese_date("2023年12月25日", base_date) == datetime(2023, 12, 25)
    
    # 测试MM月DD日格式
    assert parse_chinese_date("12月25日", base_date) == datetime(2023, 12, 25)
    assert parse_chinese_date("12月25", base_date) == datetime(2023, 12, 25)
    
    # 测试中文月份和日期
    assert parse_chinese_date("十二月二十五日", base_date) == datetime(2023, 12, 25)
    assert parse_chinese_date("十二月二十五", base_date) == datetime(2023, 12, 25)
    
    # 测试中文数字日期
    assert parse_chinese_date("一月一日", base_date) == datetime(2023, 1, 1)
    assert parse_chinese_date("二月二日", base_date) == datetime(2023, 2, 2)


def test_parse_holiday():
    """测试节假日识别"""
    # 测试元旦
    assert parse_holiday("元旦", 2023) == datetime(2023, 1, 1)
    
    # 测试劳动节
    assert parse_holiday("劳动节", 2023) == datetime(2023, 5, 1)
    
    # 测试国庆节
    assert parse_holiday("国庆节", 2023) == datetime(2023, 10, 1)


def test_search_relative_date(authenticated_client):
    """测试相对日期搜索"""
    # 测试搜索今天的事件
    response = authenticated_client.get('/?search=今天')
    assert response.status_code == 200
    assert 'Bob' in response.text
    assert 'Alice' not in response.text
    assert 'Charlie' not in response.text
    
    # 测试搜索昨天的事件
    response = authenticated_client.get('/?search=昨天')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' not in response.text
    assert 'Charlie' not in response.text
    
    # 测试搜索明天的事件
    response = authenticated_client.get('/?search=明天')
    assert response.status_code == 200
    assert 'Charlie' in response.text
    assert 'Alice' not in response.text
    assert 'Bob' not in response.text
    
    # 测试搜索3天前的事件（应该没有结果）
    response = authenticated_client.get('/?search=3天前')
    assert response.status_code == 200
    assert '暂无共同房间事件' in response.text


def test_search_chinese_date(authenticated_client):
    """测试中文日期搜索"""
    # 测试搜索具体日期
    today = datetime.now().strftime('%Y-%m-%d')
    response = authenticated_client.get(f'/?search={today}')
    assert response.status_code == 200
    assert 'Bob' in response.text
    
    # 测试搜索中文日期格式
    today_chinese = datetime.now().strftime('%Y年%m月%d日')
    response = authenticated_client.get(f'/?search={today_chinese}')
    assert response.status_code == 200
    assert 'Bob' in response.text


def test_search_holiday(authenticated_client):
    """测试节假日搜索"""
    # 测试搜索国庆节
    response = authenticated_client.get('/?search=国庆节')
    assert response.status_code == 200
    # 应该返回空结果，因为我们的测试数据中没有国庆节的事件
    
    # 测试搜索劳动节
    response = authenticated_client.get('/?search=劳动节')
    assert response.status_code == 200
    # 应该返回空结果，因为我们的测试数据中没有劳动节的事件


def test_search_multiple_conditions(authenticated_client):
    """测试多条件搜索"""
    # 测试组合搜索：关键词 + 日期
    response = authenticated_client.get('/?search=Alice 昨天')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' not in response.text
    
    # 测试组合搜索：多个关键词
    response = authenticated_client.get('/?search=Alice Social')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' in response.text
    assert 'Charlie' in response.text
    
    # 测试组合搜索：相对日期 + 标签
    response = authenticated_client.get('/?search=今天 Social')
    assert response.status_code == 200
    assert 'Bob' in response.text
    assert 'Alice' not in response.text
    assert 'Charlie' not in response.text


def test_fuzzy_search(authenticated_client):
    """测试模糊搜索"""
    # 测试前缀匹配
    response = authenticated_client.get('/?search=Alic')
    assert response.status_code == 200
    assert 'Alice' in response.text
    
    # 测试后缀匹配
    response = authenticated_client.get('/?search=ice')
    assert response.status_code == 200
    assert 'Alice' in response.text
    
    # 测试子串匹配
    response = authenticated_client.get('/?search=lic')
    assert response.status_code == 200
    assert 'Alice' in response.text
    
    # 测试短关键词匹配
    response = authenticated_client.get('/?search=A')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' in response.text
    assert 'Charlie' in response.text
