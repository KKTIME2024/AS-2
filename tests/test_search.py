import pytest
from datetime import datetime, timedelta
from app import app, db, User, World, SharedEvent, EventTag


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
        test_user = User(
            username="testuser",
            password_hash=generate_password_hash("testpass"))
        db.session.add(test_user)
        db.session.commit()

        # 创建测试世界
        world1 = World(world_name="Test World 1", tags="Social,Music,Dance")
        world2 = World(world_name="Test World 2", tags="Game,Horror")
        db.session.add_all([world1, world2])
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
            world_id=world2.id,
            friend_name="Bob",
            start_time=now - timedelta(days=2),
            end_time=now - timedelta(days=2, hours=2),
            duration=7200
        )
        db.session.add_all([event1, event2])
        db.session.commit()

        # 添加自定义标签
        tag1 = EventTag(event_id=event1.id, tag_name="Fun")
        tag2 = EventTag(event_id=event2.id, tag_name="Scary")
        db.session.add_all([tag1, tag2])
        db.session.commit()

    # 登录用户
    client.post(
        '/login',
        data={'username': 'testuser', 'password': 'testpass'},
        follow_redirects=True
    )
    return client


def test_search_by_friend_name(authenticated_client):
    """测试按好友名称搜索"""
    response = authenticated_client.get('/?search=Alice')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' not in response.text


def test_search_by_world_name(authenticated_client):
    """测试按世界名称搜索"""
    response = authenticated_client.get('/?search=1')
    assert response.status_code == 200
    assert 'Test World 1' in response.text
    assert 'Test World 2' not in response.text


def test_search_by_world_tag(authenticated_client):
    """测试按世界标签搜索"""
    response = authenticated_client.get('/?search=Social')
    assert response.status_code == 200
    assert 'Test World 1' in response.text
    assert 'Test World 2' not in response.text


def test_search_by_custom_tag(authenticated_client):
    """测试按自定义标签搜索"""
    response = authenticated_client.get('/?search=Scary')
    assert response.status_code == 200
    assert 'Test World 2' in response.text
    assert 'Test World 1' not in response.text


def test_search_by_multiple_keywords(authenticated_client):
    """测试按多个关键词搜索"""
    response = authenticated_client.get('/?search=Alice Fun')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' not in response.text


def test_search_by_date_range(authenticated_client):
    """测试按日期范围搜索"""
    from datetime import datetime
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')

    # 搜索昨天的事件（使用日期格式）
    response = authenticated_client.get(f'/?search={yesterday}')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' not in response.text

    # 搜索两天前的事件（使用日期格式）
    response = authenticated_client.get(f'/?search={two_days_ago}')
    assert response.status_code == 200
    assert 'Bob' in response.text
    assert 'Alice' not in response.text


def test_search_with_combined_filters(authenticated_client):
    """测试组合筛选条件"""
    from datetime import datetime
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    # 使用新的搜索格式，将关键词和日期组合在一个搜索参数中
    response = authenticated_client.get(f'/?search=Alice {yesterday}')
    assert response.status_code == 200
    assert 'Alice' in response.text
    assert 'Bob' not in response.text


def test_empty_search_results(authenticated_client):
    """测试无结果的搜索"""
    response = authenticated_client.get('/?search=NonExistentUser')
    assert response.status_code == 200
    assert '暂无共同房间事件' in response.text
