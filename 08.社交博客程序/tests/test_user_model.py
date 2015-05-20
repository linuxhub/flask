#encoding:utf8

'''  功能模块测试测试 '''

import unittest
from app.models import User, AnonymousUser, Role, Permission, Follow
import time
from datetime import datetime
from app import create_app, db



class UserModelTestCase(unittest.TestCase):            
              
              def setUp(self):
                            #''' 初始化工作  '''
                            self.app = create_app('testing')
                            self.app_context = self.app.app_context()
                            self.app_context.push()
                            db.create_all()

              def tearDown(self):
                            #'''  退出清理 '''
                            db.session.remove()
                            db.drop_all()
                            self.app_context.pop()
                            
                            
              
              def test_password_setter(self):
                            #'''  密码哈希散列 结果True则通过 '''
                            u = User(password = 'cat')
                            self.assertTrue(u.password_hash is not None)
              
              def test_no_password_getter(self):
                            u = User(password = 'cat')
                            with self.assertRaises(AttributeError):
                                          u.password
                                          
              def test_password_verification(self):
                            #'''  一个正确密码 与 一个不正确密码的测试  '''
                            u = User(password = 'cat')
                            self.assertTrue(u.verify_password('cat'))     
                            self.assertFalse(u.verify_password('dog'))
                            
              def test_password_salts_are_random(self):
                            #''' 同样的密码,密码哈希散列不相同测试  '''
                            u = User(password = 'cat')
                            u2 = User(password = 'cat')
                            self.assertTrue(u.password_hash != u2.password_hash)
                            
              def test_valid_confirmation_token(self):
                            ## '''  测试 正确的用户 检验令牌  '''
                            u = User(password='cat')
                            db.session.add(u)
                            token = u.generate_confirmation_token() #生成令牌
                            self.assertTrue(u.confirm(token))      #检验令牌
                            
              def test_invalid_confirmation_token(self):
                            ## '''  测试 错误的用户 检验令牌  '''
                            u1 = User(password='cat')
                            u2 = User(password='dog')
                            db.session.add(u1)
                            db.session.add(u2)
                            db.session.commit()
                            token = u1.generate_confirmation_token()
                            self.assertFalse(u2.confirm(token))
                            

                              
              def test_expired_confirmation_token(self):
                            ## ''' 测试令牌的有过期日期  '''
                            u = User(password='cat')
                            db.session.add(u)
                            db.session.commit()
                            token = u.generate_confirmation_token(1) #过期时间1秒
                            time.sleep(2) #延时2秒
                            self.assertFalse(u.confirm(token))
                                                    
                            
              def test_valid_reset_token(self):
                            #''' 测试 有效 重置令牌 '''
                            u = User(password='cat')
                            db.session.add(u)
                            db.session.commit()
                            token = u.generate_reset_token()
                            self.assertTrue(u.reset_password(token, 'dog'))
                            self.assertTrue(u.verify_password('dog'))

              def test_invaild_reset_token(self):
                            #'''测试 无效 重置令牌    '''
                            u1 = User(password='cat')
                            u2 = User(password='dog')
                            db.session.add(u1)
                            db.session.add(u2)
                            db.session.commit()
                            token = u1.generate_reset_token()
                            self.assertFalse(u2.reset_password(token, 'horse'))
                            self.assertTrue(u2.verify_password('dog'))
                                               
                            
              def test_valid_email_change_token(self):
                            # '''  测试  更改邮件地址 生成一个令牌 模块   ''
                            u = User(email='john@example.com', password='cat')
                            db.session.add(u)
                            db.session.commit()
                            token = u.generate_email_change_token('susan@example.org')
                            self.assertTrue(u.change_email(token))
                            self.assertTrue(u.email == 'susan@example.org')
                            
                            
              def test_invalid_email_change_token(self):
                            u1 = User(email='john@example.com', password='cat')
                            u2 = User(email='susan@example.org', password='dog')
                            db.session.add(u1)
                            db.session.add(u2)
                            db.session.commit()
                            token = u1.generate_email_change_token('david@example.net')
                            self.assertFalse(u2.change_email(token))
                            self.assertTrue(u2.email == 'susan@example.org')
              
              
              def test_duplicate_email_change_token(self):
                            u1 = User(email='john@example.com', password='cat')
                            u2 = User(email='susan@example.org', password='dog')
                            db.session.add(u1)
                            db.session.add(u2)
                            db.session.commit()
                            token = u2.generate_email_change_token('john@example.com')
                            self.assertFalse(u2.change_email(token))
                            self.assertTrue(u2.email == 'susan@example.org')
              
              
              # 角色的权限单元测试 
              def test_roles_and_permissions(self):
                           
                            Role.insert_roles()
                            u = User(email='john@example.com', password='cat')
                            self.assertTrue(u.can(Permission.WRITE_ARTICLES))
                            self.assertFalse(u.can(Permission.MODERATE_COMMENTS))
              
              def test_anonymous_user(self):
                            u = AnonymousUser()
                            self.assertFalse(u.can(Permission.FOLLOW))
                            
              def test_timestamps(self):
                            u = User(password='cat')
                            db.session.add(u)
                            db.session.commit()
                            self.assertTrue(
                                          (datetime.utcnow() - u.member_since).total_seconds() < 3)
                            self.assertTrue(
                                          (datetime.utcnow() - u.last_seen).total_seconds() < 3)
              def test_ping(self):
                            u = User(password='cat')
                            db.session.add(u)
                            db.session.commit()
                            time.sleep(2)
                            last_seen_before = u.last_seen
                            u.ping()
                            self.assertTrue(u.last_seen > last_seen_before)
                

              # 用户头像              
              def test_gravatar(self):
                            u = User(email='john@example.com', password='cat')
                            with self.app.test_request_context('/'):
                                          gravatar = u.gravatar()
                                          gravatar_256 = u.gravatar(size=256)
                                          gravatar_pg = u.gravatar(rating='pg')
                                          gravatar_retro = u.gravatar(default='retro')
                            with self.app.test_request_context('/', base_url='https://example.com'):
                                          gravatar_ssl = u.gravatar()
                            self.assertTrue('http://www.gravatar.com/avatar/' +
                                            'd4c74594d841139328695756648b6bd6'in gravatar)
                            self.assertTrue('s=256' in gravatar_256)
                            self.assertTrue('r=pg' in gravatar_pg)
                            self.assertTrue('d=retro' in gravatar_retro)
                            self.assertTrue('https://secure.gravatar.com/avatar/' +
                                            'd4c74594d841139328695756648b6bd6' in gravatar_ssl)
              
              # 单元测试 用户关注 多对多 数据库关系 
              def test_follows(self):
                            u1 = User(email='john@example.com', password='cat')
                            u2 = User(email='susan@example.org', password='dog')
                            db.session.add(u1)
                            db.session.add(u2)
                            db.session.commit()
                            self.assertFalse(u1.is_following(u2))
                            self.assertFalse(u1.is_followed_by(u2))
                            
                            timestamp_before = datetime.utcnow()
                            u1.follow(u2)
                            db.session.add(u1)
                            db.session.commit()
                            timestamp_after = datetime.utcnow()
                            self.assertTrue(u1.is_following(u2))
                            self.assertFalse(u1.is_followed_by(u2))
                            self.assertTrue(u2.is_followed_by(u1))
                            self.assertTrue(u1.followed.count() == 2)
                            self.assertTrue(u2.followers.count() == 2)
                            
                            f = u1.followed.all()[-1]
                            self.assertTrue(f.followed == u2)
                            self.assertTrue(timestamp_before <= f.timestamp <= timestamp_after)
                            
                            f = u2.followers.all()[-1]
                            self.assertTrue(f.follower == u1)
                            
                            u1.unfollow(u2)
                            db.session.add(u1)
                            db.session.commit()
                            self.assertTrue(u1.followed.count() == 1)
                            self.assertTrue(u2.followers.count() == 1)
                            self.assertTrue(Follow.query.count() == 2)
                            
                            u2.follow(u1)
                            db.session.add(u1)
                            db.session.add(u2)
                            db.session.commit()
                            db.session.delete(u2)
                            db.session.commit()
                            self.assertTrue(Follow.query.count() == 1)
