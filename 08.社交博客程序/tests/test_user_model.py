#encoding:utf8

'''  密码哈希散列测试 '''

import unittest
from app.models import User


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
                                          
                            
