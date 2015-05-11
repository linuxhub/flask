#encoding:utf8

'''  数据模型  '''

from . import db
from werkzeug.security import generate_password_hash, check_password_hash  #密码哈希散列

# pip install flask-login #用户登录
from flask.ext.login import UserMixin 
from . import login_manager

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #用户注册确认验证令牌
from flask import current_app


#定义Role模型
class Role(db.Model):
              __tablename__ = 'roles'                       #表名
              id = db.Column(db.Integer, primary_key=True)  #列名
              name = db.Column(db.String(64), unique=True)  #列名
              #users = db.relationship('User', backref='role') 
              users = db.relationship('User', backref='role', lazy='dynamic') # dynamic禁止自动执行查询

              def __repr__(self):
                            return '<Role %r>' % self.name

#定义User模型 
class User(UserMixin, db.Model):
              __tablename__ = 'users'                                       #表名 users
              id = db.Column(db.Integer, primary_key=True)                  #列名 id
              email = db.Column(db.String(64), unique=True, index=True)     #列名 email （用户使用电子邮件进行登录）
              username = db.Column(db.String(64), unique=True, index=True)  #列名 username  
              password_hash = db.Column(db.String(128))                     #列名: 密码哈希散列
              confirmed = db.Column(db.Boolean, default=False)              #列名: 注册用户确认 (1表示已验证, 0表示没有验证)
              role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))    


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
              
              def generate_confirmation_token(self, expiration=1):
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
                
                
              def __repr__(self):
                            return '<Role %r>' % self.username
              


#加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
              '''  如果找到用户,返回用户对象,否则返回 None  '''
              return User.query.get(int(user_id))

              


