#encoding:utf8

'''  使用Selenium 运行测试的框架  '''



import re
import threading
import unittest
from selenium import webdriver
from app import create_app, db
from app.models import Role, User, Post


class SeleniumTestCase(unittest.TestCase):
              client = None

              @classmethod
              def setUpClass(cls):
                            # 启动Firefox
                            try:
                                          cls.client = webdriver.Firefox()
                            except:
                                          pass
              
                            # 如果无法启动浏览器,则跳过这些测试
                            if cls.client:
                                          # 创建程序 
                                          cls.app = create_app('testing')
                                          cls.app_context = cls.app.app_context()
                                          cls.app_context.push()
                                          
                                          # 禁止日志,保持输出简洁
                                          import logging
                                          logger = logging.getLogger('werkzeug')
                                          logger.setLevel("ERROR")
              
                                          #创建数据库,并使用一些虚拟数据填充
                                          db.create_all()
                                          Role.insert_roles()
                                          User.generate_fake(10)
                                          Post.generate_fake(10)
              
                                           # 添加管理员
                                          admin_role = Role.query.filter_by(permissions=0xff).first()
                                          admin = User(email='john@example.com',
                                                       username='john', password='cat',
                                                       role=admin_role, confirmed=True)
                                          db.session.add(admin)
                                          db.session.commit()
              
                                          # 在一个线程中启动Flask服务器
                                          threading.Thread(target=cls.app.run).start()
                            
              
              @classmethod
              def tearDownClass(cls):
                            if cls.client:
                                          #关闭Flask服务器和浏览器
                                          cls.client.get('http://localhost:5000/shutdown')
                                          cls.client.close()

                                           #销毁数据库
                                          db.drop_all()
                                          db.session.remove()

                                           #删除程序上下文
                                          cls.app_context.pop()
                                          
              def setUp(self):
                            if not self.client:
                                          self.skipTest('Web browser not available')                     

              def tearDown(self):
                            pass

              def test_admin_home_page(self):
                            # 进入首页
                            self.client.get('http://localhost:5000/')
                            self.assertTrue(re.search('Hello,\s+Stranger!',
                                                      self.client.page_source))

                            # 进入登录页面
                            self.client.find_element_by_link_text('登录').click()
                            self.assertTrue(u'<h1>用户登录页面</h1>' in self.client.page_source)

                            # 登录
                            self.client.find_element_by_name('email').\
                                          send_keys('john@example.com')
                            self.client.find_element_by_name('password').send_keys('cat')
                            self.client.find_element_by_name('submit').click()
                            self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

                            # 进入用户资料页面
                            self.client.find_element_by_link_text(u'资料').click()
                            self.assertTrue('<h1>john</h1>' in self.client.page_source)
                            