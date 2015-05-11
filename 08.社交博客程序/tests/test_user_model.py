#encoding:utf8

'''  密码哈希散列测试 '''

import unittest
from app.models import User
import time
from app import create_app, db


class UserModelTestCase(unittest.TestCase):
              
              def test_password_setter(self):
                            #'''  密码哈希散列 结果True则通过 '''
                            u = User(password = 'zeping')
                            self.assertTrue(u.password_hash is not None)
              
              def test_no_password_getter(self):
                            u = User(password = 'zeping')
                            with self.assertRaises(AttributeError):
                                          u.password
                                          
              def test_password_verification(self):
                            #'''  一个正确密码 与 一个不正确密码的测试  '''
                            u = User(password = 'zeping')
                            self.assertTrue(u.verify_password('zeping'))     
                            self.assertFalse(u.verify_password('linuxhub'))
                            
              def test_password_salts_are_random(self):
                            #''' 同样的密码,密码哈希散列不相同测试  '''
                            u = User(password = 'zeping')
                            u2 = User(password = 'zeping')
                            self.assertTrue(u.password_hash != u2.password_hash)
                            
              def test_valid_confirmation_token(self):
                            ## '''  测试 正确的用户 检验令牌  '''
                            u = User(password='zeping')
                            db.session.add(u)
                            token = u.generate_confirmation_token() #生成令牌
                            self.assertTrue(u.confirm(token))      #检验令牌
                            
              def test_invalid_confirmation_token(self):
                            ## '''  测试 错误的用户 检验令牌  '''
                            u1 = User(password='zeping')
                            u2 = User(password='linuxhub')
                            db.session.add(u1)
                            db.session.add(u2)
                            db.session.commit()
                            token = u1.generate_confirmation_token()
                            self.assertFalse(u2.confirm(token))
                            

                              
              def test_expired_confirmation_token(self):
                            ## ''' 测试令牌的有过期日期  '''
                            u = User(password='zeping')
                            db.session.add(u)
                            db.session.commit()
                            token = u.generate_confirmation_token(1) #过期时间1秒
                            time.sleep(2) #延时2秒
                            self.assertFalse(u.confirm(token))
             
