#encoding:utf8

''' 创建蓝本 auth '''

from flask import Blueprint

auth = Blueprint('auth', __name__)  #蓝本名称: auth

from . import views   #app/auth/views.py模块引入蓝本 
