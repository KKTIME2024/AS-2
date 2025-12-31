import pytest
from datetime import datetime, timedelta
from app import app, db, User, SharedEvent, World


@pytest.fixture
def client():
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
    # 在测试数据库中创建用户，使用哈希密码
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        test_user = User(username="testuser", password_hash=generate_password_hash("testpass"))
        db.session.add(test_user)
        db.session.commit()

    # 登录用户
    client.post(
        '/login',
        data={
            'username': 'testuser',
            'password': 'testpass'},
        follow_redirects=True)
    return client


def test_login_page(client):
    """测试登录页面是否正常访问"""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()


def test_register(client):
    """测试注册功能"""
    # 测试GET请求
    response = client.get('/register')
    assert response.status_code == 200

    # 测试POST请求 - 注册新用户
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpass'
    }, follow_redirects=True)
    assert response.status_code == 200


def test_index_authenticated(authenticated_client):
    """测试已认证用户可以访问主页"""
    response = authenticated_client.get('/')
    assert response.status_code == 200


def test_index_unauthenticated(client):
    """测试未认证用户访问主页会被重定向到登录页面"""
    response = client.get('/')
    assert response.status_code == 302  # 重定向到登录页面
    assert '/login' in response.location





def test_add_tag(authenticated_client):
    """测试添加标签功能"""
    event_id = None

    # 创建测试数据
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        world = World(world_name="Test World")
        db.session.add(world)
        db.session.commit()

        event = SharedEvent(
            user_id=user.id,
            world_id=world.id,
            friend_name="Test Friend",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            duration=3600  # 1小时
        )
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    # 测试添加标签
    response = authenticated_client.post(f'/event/{event_id}/tags', data={
        'tag_name': 'testtag'
    }, follow_redirects=True)
    assert response.status_code == 200

    # 验证标签被添加
    with app.app_context():
        updated_event = SharedEvent.query.get(event_id)
        assert len(updated_event.custom_tags) == 1
        assert updated_event.custom_tags[0].tag_name == 'testtag'
