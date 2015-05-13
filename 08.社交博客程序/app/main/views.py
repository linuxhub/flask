#encoding:utf8

'''  蓝本中定义路由程序  '''

from flask import render_template, abort
from . import main            #main蓝本
from ..models import User     #数据模型


#蓝本.路由
@main.route('/')
def index():
    return render_template('index.html')


#用户资料页面的路由
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    #如果用户不存在则返回404错误
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


