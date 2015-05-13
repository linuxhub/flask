#encoding:utf8

''' 创建蓝本 main '''

from flask import Blueprint

main = Blueprint('main', __name__)  #这个蓝本的名称叫 main

from . import views, errors   #蓝本中处理的 路由 与 错误程序 
                              #app/main/views.py模块引入蓝本 
                              #app/main/erros.py模块引入蓝本

#app/__init_.py中注册蓝本


from ..models import Permission

#把Permission类加入模板上下文
#上下文处理器能让变量在所有模板中全局可访问
@main.app_context_processor
def inject_permissions():
              return dict(Permission=Permission)