#encoding:utf8

'''  数据模型  '''

from . import db
from werkzeug.security import generate_password_hash, check_password_hash  #密码哈希散列

# pip install flask-login #用户登录
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import login_manager

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #用户注册确认验证令牌
from flask import current_app, request, url_for
from datetime import datetime

#把Markdown文本转换成HTML
import bleach 
from markdown import markdown


#显示Gravatar头像所需要的
import hashlib
from flask import request 

from app.exceptions import ValidationError



class Permission:
              ''' 权限常量 （程序的权限） '''
              FOLLOW = 0x01            #关注用户（关注其他用户）
              COMMENT = 0x02           #在他人的文章中发表评论 （在他人撰写的文章中发布评论）
              WRITE_ARTICLES = 0x04    #写文章  （写原创文章）
              MODERATE_COMMENTS = 0x08 #管理他人发表的评论 （删除他人发表的不当评论）
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

# 关注关联表模型
class Follow(db.Model):
              __tablename__ = 'follows'
              follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) #自己     (左边)
              followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) #关注了谁 (右边)
              timestamp = db.Column(db.DateTime, default=datetime.utcnow) #日期时间


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
              #显示Gravatar头像所需要的              
              avatar_hash = db.Column(db.String(32))  #Gravatar头像生成的MD5值
              posts = db.relationship('Post', backref='author', lazy='dynamic') #外链到posts文章表
  
              
              # 使用两个 一对多的关系实现的多对多的关系 【关注用户】
              # 左边(自己)              
              followed = db.relationship('Follow',
                                         foreign_keys=[Follow.follower_id],             #foreign_keys参数指定外键,防止外键间的歧义
                                         backref=db.backref('follower', lazy='joined'), #lazy='joined'  加载记录,但使用联结
                                         lazy='dynamic',                                #lazy='dynamic' 不加载记录，但提供加载记录的查询
                                         cascade='all, delete-orphan')                  #启用所有默认层叠选项,而且删除孤儿记录
              # 右边(关注了谁)
              followers = db.relationship('Follow',
                                          foreign_keys=[Follow.followed_id],
                                          backref=db.backref('followed', lazy='joined'),
                                          lazy='dynamic',
                                          cascade='all, delete-orphan')
              
              #用户评论 users表与comments表之间的一对多关系
              comments = db.relationship('Comment', backref='author', lazy='dynamic')

              
              #定义默认的用户角色
              def __init__(self, **kwargs):
                            '''  根据配置文件中定义的管理员邮箱（FLASKY_ADMIN）来给该用户自动赋值成管理员权限 '''
                            super(User, self).__init__(**kwargs)
                            if self.role is None:
                                          if self.email == current_app.config['FLASKY_ADMIN']:
                                                        self.role = Role.query.filter_by(permissions=0xff).first()
                                          if self.role is None:
                                                        self.role = Role.query.filter_by(default=True).first()
                            
                            #下面部分是缓存的Gravatar头像的产生MD5值
                            if self.email is not None and self.avatar_hash is None:
                                                        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
                                                        
                            #构建用户时把自己设为自己的粉丝(这样就可以在首页文章我关注的文章中看到自己的文章)
                            #self.follow(self)
                            self.followed.append(Follow(followed=self))
                            
                            

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
                            
                            #下面这条是缓存的Gravatar头像的相关的
                            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest() #更换邮件地址后重新创建头像的md5值
                            
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
                 
              
              #生成Gravatar头像的URL
              def gravatar(self, size=100, default='identicon', rating='g'):
                            '''  生成Gravatar头像URL '''
                            if request.is_secure:
                                          url = 'https://secure.gravatar.com/avatar'
                            else:
                                          url = 'http://www.gravatar.com/avatar'
                            #hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
                            hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
                            
                            return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)
                            #例: URL结果: http://www.gravatar.com/avatar/572bc94368fec49fab782b6cda3a3597?s=100&d=identicon&r=g
               
               
               
              #生成虚拟用户（在做分页功能的时候需要大量的测试数据）
              ''' 使用: python manage.py shell
                       User.generate_fake(100)
              '''
              @staticmethod
              def generate_fake(count=100):
                            from sqlalchemy.exc import IntegrityError
                            from random import seed
                            import forgery_py

                            seed()
                            for i in range(count):
                                          u = User(email=forgery_py.internet.email_address(),
                                                   username=forgery_py.internet.user_name(True),
                                                   password=forgery_py.lorem_ipsum.word(),
                                                   confirmed=True,
                                                   name=forgery_py.name.full_name(),
                                                   location=forgery_py.address.city(),
                                                   about_me=forgery_py.lorem_ipsum.sentence(),
                                                   member_since=forgery_py.date.date(True))
                                          db.session.add(u)
                                          try:
                                                        db.session.commit()
                                          except IntegrityError:
                                                        db.session.rollback()
                              
              # 关注关系的辅助方法 
              def follow(self, user):
                            ''' 关注 '''
                            if not self.is_following(user):
                                          f = Follow(followed=user)
                                          #db.session.add(f)
                                          self.followed.append(f)
              
              def unfollow(self, user):
                            ''' 取消关注 '''
                            f = self.followed.filter_by(followed_id=user.id).first()
                            if f:             
                                          #db.session.delete(f)
                                          self.followed.remove(f)

              def is_following(self, user):
                            ''' 左边(关注者)的一对多关系中搜索指定用户,如果找到就返回True'''
                            return self.followed.filter_by(followed_id=user.id).first() is not None

              def is_followed_by(self, user):
                            ''' 右边(被关注者)的一对多关系中搜索指定用户,如果找到就返回True  '''
                            return self.followers.filter_by(follower_id=user.id).first() is not None   
              
              #获取所关注的用户文章
              @property
              def followed_posts(self):
                            ''' 获取所关注的用户文章 [联接查询] '''
                            return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)
              
              
              #把用户设为自己的关注者(用来更新数据库有原来数据，需要手动执行)
              @staticmethod
              def add_self_follows():
                            '''  
                            解决之前的数据库没有将自己设置为自己的粉丝.
                            需在手动来执行,使用方法如下: 
                                 python manage.py shell
                                 User.add_self_follows()
                            '''                            
                            for user in User.query.all():
                                          if not user.is_following(user):
                                                        user.follow(user)
                                                        db.session.add(user)
                                                        db.session.commit()
                                                        
              # 客户端API 支持基于令牌的认证
              def generate_auth_token(self, expiration):
                            ''' 使用编码后的用户id字段值生成一签名令牌,还指定了以秒为单位的过期时间 '''
                            s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
                            return s.dumps({'id': self.id}).decode('ascii')
              @staticmethod
              def verify_auth_token(token):
                            ''' 接受的参数是一个令牌,如果令牌可用就返回对应的用户
                                这是静态方法,因为只有解码令牌后才知道用户是谁
                            '''
                            s = Serializer(current_app.config['SECRET_KEY'])
                            try:
                                          data = s.loads(token)
                            except:
                                          return None
                            return User.query.get(data['id'])
              
              #把用户转换成JSON格式的序列化字典(api相关)
              def to_json(self):
                            json_user = {
                                          'url': url_for('api.get_post', id=self.id, _external=True),
                                          'username': self.username,
                                          'member_since': self.member_since,
                                          'last_seen': self.last_seen,
                                          'posts': url_for('api.get_user_posts', id=self.id, _external=True),
                                          'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
                                          'post_count': self.posts.count()
                            }
                            return json_user
              
              
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

              


#定义文章模型
class Post(db.Model):
              __tablename__ = 'posts'  #表名: posts
              id = db.Column(db.Integer, primary_key=True)  #列名： 文章id 
              body = db.Column(db.Text)                     #列名:  文章内容                         
              timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) #列名：时间戳
              author_id = db.Column(db.Integer, db.ForeignKey('users.id'))     #作者id 链接到users表的id
              body_html = db.Column(db.Text)      #列名: 博客文章HTML代码缓存（处理Markdown文本）
              
              #用户评论  posts表与comments表之间的一对多关系               
              comments = db.relationship('Comment', backref='post', lazy='dynamic')
              
              
              #生成虚拟博客文章 （在做分页功能的时候需要大量的测试数据）
              ''' 使用: python manage.py shell
                        Post.generate_fake(100)
              '''              
              @staticmethod
              def generate_fake(count=100):
                            from random import seed, randint
                            import forgery_py

                            seed()
                            user_count = User.query.count()
                            for i in range(count):
                                          u = User.query.offset(randint(0, user_count - 1)).first()
                                          p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                                                   timestamp=forgery_py.date.date(True),
                                                   author=u)
                                          db.session.add(p)
                                          db.session.commit()
                          
                                          
              #在Post模型中处理Markdown文本
              @staticmethod
              def on_changed_body(target, value, oldvalue, initiator):
                            ''' 把body字段中的文本渲染成HTML格式,结果保存在body_html中,自动且高效地完成Markdown文本到时HTML的转换  '''
                            allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li' , 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
                            target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))
               # *备注: <pre> 看到时这标签你想起来了吧,是什么做用了吧. 写博客文章高亮代码常用用标签.. 哈哈  
               
               
              #把文章和json的序列转换(api相关)
              def to_json(self):
                            json_post = {
                                          'url': url_for('api.get_post', id=self.id, _external=True),
                                          'body': self.body,
                                          'body_html': self.body_html,
                                          'timestamp': self.timestamp,
                                          'author': url_for('api.get_user', id=self.author_id, _external=True),
                                          'comments': url_for('api.get_post_comments', id=self.id, _external=True),
                                          'comment_count': self.comments.count()
                            }
                            return json_post
 
              #从JSON格式数据创建一篇博客文章
              @staticmethod
              def from_json(json_post):
                            body = json_post.get('body')
                            if body is None or body == '':
                                          raise ValidationError(u'文章没有内容')
                            return Post(body=body)
                            
              
db.event.listen(Post.body, 'set', Post.on_changed_body) #只要这个类实例的body字段设了新值,函数就会自动被调用.




# 用户评论 Comment模型
class Comment(db.Model):
              __tablename__ = 'comments'
              id = db.Column(db.Integer, primary_key=True)
              body = db.Column(db.Text)
              body_html = db.Column(db.Text)
              timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
              disabled = db.Column(db.Boolean)
              author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
              post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
              
              
              #把Markdown文本转成HTML 保存到body_html
              @staticmethod
              def on_changed_body(target, value, oldvalue, initiator):
                            allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
                            target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'),tags=allowed_tags, strip=True))




              #把评论和json的序列转换(api相关)
              def to_json(self):
                            json_comment = {
                                          'url': url_for('api.get_comment', id=self.id, _external=True),
                                          'post': url_for('api.get_post', id=self.post_id, _external=True),
                                          'body': self.body,
                                          'body_html': self.body_html,
                                          'timestamp': self.timestamp,
                                          'author': url_for('api.get_user', id=self.author_id,
                                                            _external=True),
                            }
                            return json_comment
              
              #从JSON格式数据生成评论
              @staticmethod
              def from_json(json_comment):
                            body = json_comment.get('body')
                            if body is None or body == '':
                                          raise ValidationError(u'没有评论内容')
                            return Comment(body=body)              

#在修改body字段内容时触发, #把Markdown文本转成HTML
db.event.listen(Comment.body, 'set', Comment.on_changed_body)