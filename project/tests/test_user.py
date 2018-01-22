import json
from project.tests.base import BaseTestCase
from project.api.models import User
from project import db



def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    def test_users(self):
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """确保添加用户成功"""
        with self.client:
            response = self.client.post(
                '/users',
                data = json.dumps(dict(username='cnych', email='123@qq.com')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('123@qq.com was added', data['message'])
            self.assertEqual('success', data['status'])

    def test_add_user_invalid_json(self):
        """测试post的数据为空"""
        with self.client:
            response = self.client.post(
                '/users',
                data = json.dumps(dict()),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """如果JSON对象中没有username或email，确保抛出一个错误。"""
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(email='qikqiak@gmail.com')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(username='cnych')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_duplicate_user(self):
        """验证添加重复的用户"""
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(username='cnych', email='123@qq.com')),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(username='cnych', email='123@qq.com')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That email already exists.', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user(self):
        """测试获取单个用户详细信息"""
        user=User(username='cnych', email='123@qq.com')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get('/users/%d' % user.id)
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertEqual('cnych', data['data']['username'])
            self.assertEqual('123@qq.com', data['data']['email'])
            self.assertEqual('success', data['status'])

    def test_get_user_no_id(self):
        """如果没有id的时候抛出异常。"""
        with self.client:
            response = self.client.get('/users/xxx')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Param id error', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user_incorrect_id(self):
        """如果ID不存在则要抛出异常"""
        with self.client:
            response = self.client.get('/users/-1')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_users(self):
        """测试获取用户列表"""
        user1=User(username='cnych', email='123@qq.com')
        user2=User(username='cnych1', email='1231@qq.com')
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        with self.client:
            response = self.client.get('/users')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual('cnych' , data['data']['users'][0]['username'])
            self.assertEqual('1231@qq.com' , data['data']['users'][1]['email'])
            self.assertEqual('success', data['status'])

    def test_main_no_users(self):
        """没有用户"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No users!', response.data)

    def test_main_with_users(self):
        """有多个用户的场景"""
        add_user('cnych', 'icnych@gmail.com')
        add_user('qikqiak', 'qikqiak@gmail.com')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertNotIn(b'No users!', response.data)
        self.assertIn(b'cnych', response.data)
        self.assertIn(b'qikqiak', response.data)

    def test_main_add_user(self):
        """前端页面添加一个新的用户"""
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='cnych', email='cnych@gmail.com'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'No users!', response.data)
            self.assertIn(b'cnych', response.data)

