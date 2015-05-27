#encoding:utf8

'''
   构造文件
   使用了工厂函数,可以动态加载配置
'''

from flask import Flask, render_template     #Flask框架与模板
from flask.ext.bootstrap import Bootstrap    #Bootstrap
from flask.ext.mail import Mail              #邮件
from flask.ext.moment import Moment          #时间和日期 
from flask.ext.sqlalchemy import SQLAlchemy  #数据操作
from config import config    #加载配置文件(app/config.py)
from flask.ext.login import LoginManager     #用户登录
from flask.ext.pagedown import PageDown      #富文本文章功能


#初始化
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()  

#初始化Flask-Login
login_manager = LoginManager()
login_manager.session_protection = 'strong' #设置安全级别为"strong",Flask-Login会记录客户端IP地址和浏览器的用户代理信息,如果发现异动就退出用户.
login_manager.login_view = 'auth.login'     #设置登录用户页面的端点.(登录路由在auth蓝本中定义,所以前面要加上蓝本的名字)


def create_app(config_name):
    
    ''' 工厂函数 '''
    
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)        #初始化Flask-PageDown
        
    #注册 main蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    #注册 auth蓝本
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    #url_prefix='/auth' 是可选参数,如果使用了,所有的路由都要加止前缀 
    #上面这个URL就变成了:  http://127.0.0.1:5000/auth/login
    
    # 注册API蓝本
    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')    
    
    return app



