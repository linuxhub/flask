#encoding:utf8

'''
   3个运行环境配置
   每个不同的运行环境使用不同的数据库
'''

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'  #跨站请求伪造保护 密钥
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True   #每次请求结束后都会自动提交数据库中的变动
    
    #分页文章列表 
    FLASKY_POSTS_PER_PAGE = 20   #默认20行
    
    #用户的关注与用户粉丝的列表分页默认数
    FLASKY_FOLLOWERS_PER_PAGE = 50 #默认50行
    
    
    #控制每页显示的评论数量
    FLASKY_COMMENTS_PER_PAGE = 30  #评论默认30行

    #数据库慢查询【性能】启用慢查询记录功能
    SQLALCHEMY_RECORD_QUERIES = True    #启用记录查询统计数字的功能
    FLASKY_SLOW_DB_QUERY_TIME = 0.5     #慢查询的时间阈值为0.5秒

     

    #邮箱发送配置
    MAIL_SERVER = 'smtp.163.com' #163邮箱  smtp
    MAIL_PORT = 465              #163邮箱 端口
    MAIL_USE_TLS = False         #TLS协议
    MAIL_USE_SSL = True          #SSL协议(开启)

    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_USERNAME = 'zepingmon'  #邮箱 用户名

    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_PASSWORD = '123456789'  #邮箱 密码
    
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flask]' #邮件主题前缀
    #FLASKY_MAIL_SENDER = 'Flasky Admin <zepingmon@163.com>' #发件人
    FLASKY_MAIL_SENDER = 'Flasky Admin <zepingmon@163.com>' #发件人

    #FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    FLASKY_ADMIN = 'root@linuxhub.org'    #收件人 【管理员】 
    
    @staticmethod  #静态方法
    def init_app(app):
        pass
   
   
    
class DevelopmentConfig(Config):
    '''  开发环境  '''   
    DEBUG = True    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    '''  测试环境  '''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite') 
    WTF_CSRF_ENABLED = False  #测试配置中禁用CSRF保护

class ProductionConfig(Config):
    ''' 生产环境 '''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite') 
    
    # 程序出错时发送电子邮件（错误信息不是界面端显示）
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # 把错误通过电子邮件发送给管理员
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.FLASKY_MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'devlopment': DevelopmentConfig, #开发环境
    'testing': TestingConfig,        #测试环境
    'production': ProductionConfig,  #生产环境
    'default': DevelopmentConfig     #默认是开发环境
}
    
    
