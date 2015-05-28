#encoding:utf8

'''  测试客户端编写的单元测试框架   '''


import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
              def setUp(self):
                            self.app = create_app('testing')
                            self.app_context = self.app.app_context()
                            self.app_context.push()
                            db.create_all()
                            Role.insert_roles()
                            self.client = self.app.test_client(use_cookies=True) #测试客户端对象 （启用cookie像浏览器一样可能接收和发半发送cookie）

              def tearDown(self):
                            db.session.remove()
                            db.drop_all()
                            self.app_context.pop()
              
              #测试作为一个简单的例子演示了测试客户端的作用
              def test_home_page(self):
                            response = self.client.get(url_for('main.index'))
                            self.assertTrue(b'Stranger' in response.data) #为了检查测试是否成功,要在响应主体中搜索是否包含“Stranger”这个词
                            

        
              def test_register_and_login(self):
                            # 注册新帐户
                            response = self.client.post(url_for('auth.register'), data={
                                          'email': 'john@example.com',
                                          'username': 'john',
                                          'password': 'cat',
                                          'password2': 'cat'
                            })
                            self.assertTrue(response.status_code == 302)

                            # 使用新注册的账户登录
                            response = self.client.post(url_for('auth.login'), data={
                                          'email': 'john@example.com',
                                          'password': 'cat'
                                          }, follow_redirects=True)
                            
                            self.assertTrue(re.search(b'john+,您好!', response.data))             #抓取网页内容(app/templates/index.html文件中的内容)
                            self.assertTrue(b'你的邮箱还未验证,请尽快查收邮件.' in response.data)  #抓取网页内容(app/templates/auth/unconfirmed.html文件中的内容)
 
                            # 发送确认令牌
                            user = User.query.filter_by(email='john@example.com').first()
                            token = user.generate_confirmation_token()
                            response = self.client.get(url_for('auth.confirm', token=token),follow_redirects=True)
                            self.assertTrue(b'帐号已验证!' in response.data)  #抓取网页内容 (app/auth/views.py文件中的内容)

                            # 退出
                            response = self.client.get(url_for('auth.logout'), follow_redirects=True)
                            self.assertTrue(b'用户已退出' in response.data)   #抓取网页内容 (app/auth/views.py文件中的内容)
