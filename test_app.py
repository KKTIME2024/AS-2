import unittest
from app import app, db, User, SharedEvent, World, EventComment
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime


class TestVRChatMemories(unittest.TestCase):
    """VRChat记忆记录器测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 使用内存数据库
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()

        with app.app_context():
            db.create_all()
            
            # 创建测试用户，使用正确的密码哈希
            test_user = User(username='testuser', password_hash=generate_password_hash('password'))
            db.session.add(test_user)
            db.session.commit()
            self.test_user_id = test_user.id

            # 创建测试世界
            test_world = World(
                world_name='Test World',
                world_id='test-world-id',
                tags='test,world')
            db.session.add(test_world)
            db.session.commit()
            self.test_world_id = test_world.id

    def tearDown(self):
        """测试后的清理工作"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_home_page(self):
        """测试首页访问"""
        response = self.app.get('/')
        # 未登录用户应该重定向到登录页面
        self.assertEqual(response.status_code, 302)

    def test_login_page(self):
        """测试登录页面访问"""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('登录', response.get_data(as_text=True))

    def test_register_page(self):
        """测试注册页面访问"""
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn('注册', response.get_data(as_text=True))

    def test_create_event(self):
        """测试创建事件"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 创建事件
        response = self.app.post('/event/create', data={
            'friend_name': 'Test Friend',
            'world_name': 'Test World',
            'world_tags': 'test,tag',
            'start_time': '2023-01-01T10:00',
            'end_time': '2023-01-01T12:00',
            'notes': 'Test notes'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_get_events(self):
        """测试获取事件列表"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 创建一个事件用于测试
        with app.app_context():
            event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Test Friend',
                start_time=datetime(2023, 1, 1, 10, 0),
                end_time=datetime(2023, 1, 1, 12, 0),
                duration=7200
            )
            db.session.add(event)
            db.session.commit()

        # 获取事件列表
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_event_detail(self):
        """测试事件详情页面"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 创建一个事件用于测试
        with app.app_context():
            event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Test Friend',
                start_time=datetime(2023, 1, 1, 10, 0),
                end_time=datetime(2023, 1, 1, 12, 0),
                duration=7200
            )
            db.session.add(event)
            db.session.commit()
            event_id = event.id

        # 访问事件详情页面
        response = self.app.get(f'/event/{event_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Friend', response.get_data(as_text=True))

    def test_comment_system(self):
        """测试评论系统"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 创建一个事件用于测试
        with app.app_context():
            event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Test Friend',
                start_time=datetime(2023, 1, 1, 10, 0),
                end_time=datetime(2023, 1, 1, 12, 0),
                duration=7200
            )
            db.session.add(event)
            db.session.commit()
            event_id = event.id

        # 添加评论
        comment_data = {
            'content': 'Test comment'
        }

        response = self.app.post(
            f'/api/event/{event_id}/comments',
            data=json.dumps(comment_data),
            content_type='application/json',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        # 获取评论
        response = self.app.get(f'/api/event/{event_id}/comments')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('comments', data)

    def test_event_creation(self):
        """测试事件创建功能"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 创建事件的表单数据
        event_data = {
            'friend_name': 'Test Friend',
            'world_name': 'Test World',
            'world_tags': 'test,event',
            'start_time': '2023-01-01T10:00',
            'end_time': '2023-01-01T12:00',
            'notes': 'Test event notes'
        }

        response = self.app.post(
            '/event/create',
            data=event_data,
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 验证事件是否创建成功
        with app.app_context():
            events = SharedEvent.query.all()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].friend_name, 'Test Friend')

    def test_event_edit(self):
        """测试事件编辑功能"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 创建初始事件
        with app.app_context():
            event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Original Friend',
                start_time=datetime(2023, 1, 1, 10, 0),
                end_time=datetime(2023, 1, 1, 12, 0),
                duration=7200
            )
            db.session.add(event)
            db.session.commit()
            event_id = event.id

        # 编辑事件
        edit_data = {
            'friend_name': 'Updated Friend',
            'world_name': 'Test World',
            'world_tags': 'test,updated',
            'start_time': '2023-01-01T10:00',
            'end_time': '2023-01-01T13:00',
            'notes': 'Updated event notes'
        }

        response = self.app.post(
            f'/event/{event_id}/edit',
            data=edit_data,
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 验证事件是否更新成功
        with app.app_context():
            updated_event = SharedEvent.query.get(event_id)
            self.assertEqual(updated_event.friend_name, 'Updated Friend')

    def test_event_deletion(self):
        """测试事件删除功能"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 创建事件用于测试
        with app.app_context():
            event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Test Friend',
                start_time=datetime(2023, 1, 1, 10, 0),
                end_time=datetime(2023, 1, 1, 12, 0),
                duration=7200
            )
            db.session.add(event)
            db.session.commit()
            event_id = event.id

        # 删除事件
        response = self.app.post(
            f'/event/{event_id}/delete',
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 验证事件是否删除成功
        with app.app_context():
            deleted_event = SharedEvent.query.get(event_id)
            self.assertIsNone(deleted_event)

    def test_stats_access(self):
        """测试统计页面访问"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 访问统计页面
        response = self.app.get('/stats')
        self.assertEqual(response.status_code, 200)

    def test_visualization_access(self):
        """测试可视化页面访问"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 访问可视化API
        response = self.app.get('/api/visualization/timeline')
        self.assertEqual(response.status_code, 200)

    def test_export_events(self):
        """测试事件导出功能"""
        # 首先登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        })

        # 测试导出事件
        response = self.app.get('/api/events/export')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
