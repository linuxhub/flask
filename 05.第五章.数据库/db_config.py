#!/usr/bin/env python
#encoding:utf8
#author: linuxhub.org
# pip install flask-sqlalchemy #安装

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

#配置数据库
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')  #当前目录下的data.sqlite
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True     #每次请求结束后都会自动提交数据库中的变动
db = SQLAlchemy(app)

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

