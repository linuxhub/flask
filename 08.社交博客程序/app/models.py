#encoding:utf8

'''  数据模型  '''

from . import db



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
class User(db.Model):
              __tablename__ = 'users'                                       #表名
              id = db.Column(db.Integer, primary_key=True)                  #列名
              username = db.Column(db.String(64), unique=True, index=True)  #列名
              role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

              def __repr__(self):
                            return '<Role %r>' % self.username


