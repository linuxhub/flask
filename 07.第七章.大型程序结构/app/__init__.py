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

#初始化
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    
    ''' 工厂函数 '''
    
    app = Flask(__name__)
    
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    
    
    #注册蓝本
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app



