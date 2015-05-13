#encoding:utf8

'''  数据模型  '''

from . import db
from werkzeug.security import generate_password_hash, check_password_hash  #密码哈希散列

# pip install flask-login #用户登录
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #用户注册确认验证令牌
from flask import current_app
from datetime import datetime


class Permission:
              ''' 权限常量 （程序的权限） '''
              FOLLOW = 0x01            #关注用户（关注其他用户）
              COMMENT = 0x02           #在他人的文章中发表评论 （在他人撰写的文章中发布评论）
              WRITE_ARTICLES = 0x04    #写文章  （写原创文章）
              MODERATE_COMMENTS = 0x08 #管理他人发表的评论 （删除他人发表的不当评价）
              ADMINISTER = 0x80        #管理员权限 （管理网站）



#定义Role模型
class Role(db.Model):
              __tablename__ = 'roles'                       #表名 roles (用户角色表)
              id = db.Column(db.Integer, primary_key=True)  #列名 id
              name = db.Column(db.String(64), unique=True)  #列名 name         
              default = db.Column(db.Boolean, default=False, index=True) #列名 defaulut (默认角色) 
              permissions = db.Column(db.Integer)               #列名 permissions
              users = db.relationship('User', backref='role', lazy='dynamic') # dynamic禁止自动执行查询
              
              #用户角色权限
              ''' 把角色写入数据为，可使用shell会话
                  python manage.py shell
                  Role.insert_roles()
                  Role.query.all()
              '''
              @staticmethod
              def insert_roles():
                            ''' 
                            该函数并不是直接创建新角色对象,而是通过角色名查找现有的角色,
                            然后再进行更新. 只有当数据库中没有某个角色名时才会创建新角色对象.
                            '''
                            roles = {
                                          'User': (Permission.FOLLOW |
                                                   Permission.COMMENT |
                                                   Permission.WRITE_ARTICLES, True),
                                          'Moderator': (Permission.FOLLOW |
                                                        Permission.COMMENT |
                                                        Permission.WRITE_ARTICLES |
                                                        Permission.MODERATE_COMMENTS, False),
                                          'Administrator': (0xff, False)
                            }
                            for r in roles:
                                          role = Role.query.filter_by(name=r).first()
                                          if role is None:
                                                        role = Role(name=r)
                                          role.permissions = roles[r][0]
                                          role.default = roles[r][1]
                                          db.session.add(role)
                            db.session.commit()
                            
                            
              def __repr__(self):
                            return '<Role %r>' % self.name

#定义User模型 
class User(UserMixin, db.Model):
              __tablename__ = 'users'                                       #表名 users
              id = db.Column(db.Integer, primary_key=True)                  #列名 id
              email = db.Column(db.String(64), unique=True, index=True)     #列名 email （用户使用电子邮件进行登录）
              username = db.Column(db.String(64), unique=True, index=True)  #列名 username  
              role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))                
              password_hash = db.Column(db.String(128))                     #列名: 密码哈希散列
              confirmed = db.Column(db.Boolean, default=False)              #列名: 注册用户确认 (1表示已验证, 0表示没有验证)
              #第10章.资料信息添加以下的字段
              name = db.Column(db.String(64))                               #列名: 真实姓名   
              location = db.Column(db.String(64))                           #列名: 所在地
              about_me = db.Column(db.Text())                               #列名: 自我介绍                                     
              member_since = db.Column(db.DateTime(), default=datetime.utcnow)  #列名: 注册日期  
              last_seen = db.Column(db.DateTime(), default=datetime.utcnow)     #列名: 最后访问日期
              
              
              #定义默认的用户角色
              def __init__(self, **kwargs):
                            '''  根据配置文件中定义的管理员邮箱（FLASKY_ADMIN）来给该用户自动赋值成管理员权限 '''
                            super(User, self).__init__(**kwargs)
                            if self.role is None:
                                          if self.email == current_app.config['FLASKY_ADMIN']:
                                                        self.role = Role.query.filter_by(permissions=0xff).first()
                                          if self.role is None:
                                                        self.role = Role.query.filter_by(default=True).first()

              #用户登录
              @property  #@property作用是将方法函数变成了属性
              def password(self):
                            '''  password的只读属性(如果试图读取password属性的值,则会返回错误)  '''
                            raise AttributeError('password is not a readable attribute')
              
              
              @password.setter
              def password(self, password):
                            ''' 使用generate_password_hash()函数,将原始密码作为输入,以字符串形式输出密码的散列值,
                                将结果赋值给password_hash字段 '''
                            self.password_hash = generate_password_hash(password) 
              

              def verify_password(self, password):
                            '''  接收密码,并与password_hash中的密码散列值进行对比,如果密码正确返回True '''
                            return check_password_hash(self.password_hash, password)
              
                
              # 用户注册确认
              def generate_confirmation_token(self, expiration=3600):
                            '''  生成一个令牌 '''
                            ''' 有效默认时间为 3600秒(60分钟=1小时) '''
                            s = Serializer(current_app.config['SECRET_KEY'], expiration)
                            return s.dumps({'confirm': self.id})
              
              def confirm(self, token):
                            '''  检验令牌 '''
                            '''  如果检验通过,则把新添加的cconfirmed属性设为True'''
                            s = Serializer(current_app.config['SECRET_KEY'])
                            try:
                                          data = s.loads(token) #检验签名和过期时间
                            except:
                                          return False
                            if data.get('confirm') != self.id:
                                          return False
                            self.confirmed = True
                            db.session.add(self)
                            return True
                  
                
              def generate_reset_token(self, expiration=3600):
                            '''  重置密码  生成一个令牌  '''
                            s = Serializer(current_app.config['SECRET_KEY'], expiration)
                            return s.dumps({'reset': self.id})

              def reset_password(self, token, new_password):
                            '''  重置密码 '''
                            s = Serializer(current_app.config['SECRET_KEY'])
                            try:
                                          data = s.loads(token)
                            except:
                                          return False
                            if data.get('reset') != self.id:
                                          return False
                            self.password = new_password
                            db.session.add(self)
                            return True
              
              
              
              def generate_email_change_token(self, new_email, expiration=3600):
                            '''  更改邮件地址 生成一个令牌  '''
                            s = Serializer(current_app.config['SECRET_KEY'], expiration)
                            return s.dumps({'change_email': self.id, 'new_email': new_email})


              def change_email(self, token):
                            '''  更改邮件地址 '''
                            s = Serializer(current_app.config['SECRET_KEY'])
                            try:
                                          data = s.loads(token)
                            except:
                                          return False
                            if data.get('change_email') != self.id:
                                          return False
                            new_email = data.get('new_email')
                            if new_email is None:
                                          return False
                            if self.query.filter_by(email=new_email).first() is not None:
                                          return False
                            self.email = new_email
                            db.session.add(self)
                            return True  
              
              #【角色验证】检查用户是否有指定的权限
              def can(self, permissions):
                            ''' 该方法在请求和赋予角色这两种权限之间进行位与操作 '''
                            return self.role is not None and \
                                   (self.role.permissions & permissions) == permissions

              def is_administrator(self):
                            ''' 检查管理员权限 '''
                            return self.can(Permission.ADMINISTER)
         
              def ping(self):
                            ''' 刷新用户的最后访问时间 '''
                            self.last_seen = datetime.utcnow()
                            db.session.add(self)
                 
                       
              def __repr__(self):
                            return '<Role %r>' % self.username
              

#【角色验证】检查用户是否有指定的权限
class AnonymousUser(AnonymousUserMixin):
              ''' 
              程序不用先检查用户是否登录,
              就能自由调用current_user.can()与current_user.is_administrator 
              '''              
              def can(self, permissions):
                            return False

              def is_administrator(self):
                            return False

login_manager.anonymous_user = AnonymousUser



#加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
              '''  如果找到用户,返回用户对象,否则返回 None  '''
              return User.query.get(int(user_id))





              


