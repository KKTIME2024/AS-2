import unittest
from app import app, db, User, SharedEvent, World, EventComment, EventTag
from flask import url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta


class TestComprehensiveVRChatMemories(unittest.TestCase):
    """VRChat记忆记录器全面测试用例"""

    def setUp(self):
        """测试前的准备工作"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 使用内存数据库
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.app = app.test_client()

        with app.app_context():
            db.create_all()

            # 创建测试用户
            test_user = User(username='testuser',
                             password_hash=generate_password_hash('password'))
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

            # 创建测试事件
            test_event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Test Friend',
                start_time=datetime(2023, 1, 1, 10, 0),
                end_time=datetime(2023, 1, 1, 12, 0),
                duration=7200,
                notes='Test event notes'
            )
            db.session.add(test_event)
            db.session.commit()
            self.test_event_id = test_event.id

    def tearDown(self):
        """测试后的清理工作"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def login(self):
        """登录辅助函数"""
        return self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'  # 使用与setUp中匹配的密码
        }, follow_redirects=True)

    def test_user_registration(self):
        """测试用户注册功能"""
        # 访问注册页面
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)

        # 注册新用户
        response = self.app.post('/register', data={
            'username': 'newuser',
            'password': 'newpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 验证用户是否注册成功
        with app.app_context():
            new_user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(new_user)

    def test_user_login_logout(self):
        """测试用户登录和登出功能"""
        # 测试登录
        response = self.app.post('/login', data={
            'username': 'testuser',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 测试登出
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 验证登出后访问受保护页面会被重定向
        response = self.app.get('/')
        self.assertEqual(response.status_code, 302)  # 应该重定向到登录页面

    def test_event_list_filtering(self):
        """测试事件列表筛选功能"""
        # 登录
        self.login()

        # 创建多个事件用于测试筛选
        with app.app_context():
            for i in range(3):
                event = SharedEvent(
                    user_id=self.test_user_id,
                    world_id=self.test_world_id,
                    friend_name=f'Test Friend {i}',
                    start_time=datetime(2023, 1, i + 2, 10, 0),
                    end_time=datetime(2023, 1, i + 2, 12, 0),
                    duration=7200
                )
                db.session.add(event)
            db.session.commit()

        # 测试获取事件列表
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Friend 1', response.get_data(as_text=True))

    def test_event_search(self):
        """测试事件搜索功能"""
        # 登录
        self.login()

        # 创建带特定名称的事件
        with app.app_context():
            special_event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Special Friend',
                start_time=datetime(2023, 2, 1, 10, 0),
                end_time=datetime(2023, 2, 1, 12, 0),
                duration=7200
            )
            db.session.add(special_event)
            db.session.commit()

        # 测试搜索功能
        response = self.app.get('/?search=Special')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Special Friend', response.get_data(as_text=True))

    def test_event_tags(self):
        """测试事件标签管理"""
        # 登录
        self.login()

        # 创建带标签的事件
        with app.app_context():
            tagged_event = SharedEvent(
                user_id=self.test_user_id,
                world_id=self.test_world_id,
                friend_name='Tagged Friend',
                start_time=datetime(2023, 3, 1, 10, 0),
                end_time=datetime(2023, 3, 1, 12, 0),
                duration=7200
            )
            db.session.add(tagged_event)
            db.session.commit()

            # 添加标签
            tag = EventTag(event_id=tagged_event.id, tag_name='special-tag')
            db.session.add(tag)
            db.session.commit()

        # 测试通过标签筛选
        response = self.app.get('/?tag=special-tag')
        self.assertEqual(response.status_code, 200)

    def test_comment_creation_and_deletion(self):
        """测试评论创建和删除功能"""
        # 登录
        self.login()

        # 创建评论
        comment_data = {
            'content': 'Test comment for event'
        }

        response = self.app.post(
            f'/api/event/{self.test_event_id}/comments',
            data=json.dumps(comment_data),
            content_type='application/json',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        # 获取评论
        response = self.app.get(f'/api/event/{self.test_event_id}/comments')
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['comments']), 1)
        comment_id = data['comments'][0]['id']

        # 删除评论
        response = self.app.delete(
            f'/api/event/{self.test_event_id}/comments/{comment_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 验证评论已删除
        response = self.app.get(f'/api/event/{self.test_event_id}/comments')
        data = json.loads(response.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['comments']), 0)

    def test_comment_replies(self):
        """测试评论回复功能"""
        # 登录
        self.login()

        # 创建主评论
        main_comment_data = {
            'content': 'Main comment'
        }

        response = self.app.post(
            f'/api/event/{self.test_event_id}/comments',
            data=json.dumps(main_comment_data),
            content_type='application/json',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        main_comment_id = data['comment']['id']

        # 创建回复
        reply_data = {
            'content': 'Reply to main comment',
            'parent_id': main_comment_id
        }

        response = self.app.post(
            f'/api/event/{self.test_event_id}/comments',
            data=json.dumps(reply_data),
            content_type='application/json',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)

        # 验证回复已创建
        response = self.app.get(f'/api/event/{self.test_event_id}/comments')
        data = json.loads(response.data)
        self.assertEqual(len(data['comments'][0]['replies']), 1)

    def test_stats_endpoints(self):
        """测试统计API端点"""
        # 登录
        self.login()

        # 测试事件统计
        response = self.app.get('/api/stats/events')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_events', data)

        # 测试好友统计
        response = self.app.get('/api/stats/friends')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_friends', data)

        # 测试世界统计
        response = self.app.get('/api/stats/worlds')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_worlds', data)

    def test_visualization_endpoints(self):
        """测试可视化API端点"""
        # 登录
        self.login()

        # 测试时间线数据
        response = self.app.get('/api/visualization/timeline')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

        # 测试网络数据
        response = self.app.get('/api/visualization/network')
        self.assertEqual(response.status_code, 200)

    def test_date_range_filtering(self):
        """测试日期范围筛选功能"""
        # 登录
        self.login()

        # 创建多个不同日期的事件
        with app.app_context():
            for i in range(5):
                event = SharedEvent(
                    user_id=self.test_user_id,
                    world_id=self.test_world_id,
                    friend_name=f'Friend {i}',
                    start_time=datetime(2023, 1, i + 1, 10, 0),
                    end_time=datetime(2023, 1, i + 1, 12, 0),
                    duration=7200
                )
                db.session.add(event)
            db.session.commit()

        # 测试按日期搜索
        response = self.app.get('/?search=2023-01-03')
        self.assertEqual(response.status_code, 200)

    def test_event_creation_validation(self):
        """测试事件创建的表单验证"""
        # 登录
        self.login()

        # 测试创建无效事件（结束时间早于开始时间）
        invalid_event_data = {
            'friend_name': 'Test Friend',
            'world_name': 'Test World',
            'world_tags': 'test,event',
            'start_time': '2023-01-01T12:00',  # 开始时间晚于结束时间
            'end_time': '2023-01-01T10:00',
            'notes': 'Invalid event with wrong time order'
        }

        response = self.app.post(
            '/event/create',
            data=invalid_event_data,
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # 验证表单验证失败，页面会重新渲染
        self.assertIn('结束时间必须晚于开始时间', response.get_data(as_text=True))

    def test_event_sharing(self):
        """测试事件分享功能"""
        # 登录
        self.login()

        # 创建分享链接
        response = self.app.post(
            f'/api/event/{self.test_event_id}/share', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 解析分享链接
        data = json.loads(response.data)
        self.assertIn('share_token', data)
        share_token = data['share_token']

        # 测试访问分享链接
        response = self.app.get(f'/share/{share_token}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test Friend', response.get_data(as_text=True))

    def test_event_export_formats(self):
        """测试事件导出功能"""
        # 登录
        self.login()

        # 测试导出事件
        response = self.app.get('/api/events/export')
        self.assertEqual(response.status_code, 200)
        # 验证导出的是JSON格式
        data = json.loads(response.data)
        self.assertIn('events', data)

    def test_friend_feed(self):
        """测试好友动态功能"""
        # 登录
        self.login()

        # 获取好友动态
        response = self.app.get('/api/feed/friends')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_world_management(self):
        """测试世界管理功能"""
        # 登录
        self.login()

        # 创建事件时自动创建世界
        event_data = {
            'friend_name': 'New Friend',
            'world_name': 'New World',
            'world_tags': 'new,world',
            'start_time': '2023-03-01T10:00',
            'end_time': '2023-03-01T12:00',
            'notes': 'Event with new world'
        }

        response = self.app.post(
            '/event/create',
            data=event_data,
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # 验证世界已创建
        with app.app_context():
            new_world = World.query.filter_by(world_name='New World').first()
            self.assertIsNotNone(new_world)
            self.assertEqual(new_world.tags, 'new,world')

    def test_api_error_handling(self):
        """测试API错误处理"""
        # 登录
        self.login()

        # 测试访问不存在的事件
        response = self.app.get('/api/event/999999/like')
        self.assertEqual(response.status_code, 404)

        # 测试对不存在的事件进行评论
        comment_data = {
            'content': 'Comment on non-existent event'
        }

        response = self.app.post(
            '/api/event/999999/comments',
            data=json.dumps(comment_data),
            content_type='application/json',
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
