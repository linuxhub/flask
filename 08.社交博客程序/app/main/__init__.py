#encoding:utf8

''' 创建蓝本 '''

from flask import Blueprint

main = Blueprint('main', __name__)  #这个蓝本的名称叫 main

from . import views, errors   #蓝本中处理的 路由 与 错误程序


#app/__init_.py中注册蓝本