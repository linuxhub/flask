#!/usr/bin/env python
#encoding:utf8

'''  启动脚本  '''

import os

#代码覆盖检测所需的
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


from app import create_app, db
from app.models import User, Role, Permission, Post, Comment
from flask.ext.script import Manager, Shell  
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Post=Post, Comment=Comment)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



#启动单元测试命令
@manager.command
def test(coverage=False):
    ''' Run the unit tests '''
    
    #代码覆盖检测所需的
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
        
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    
    #代码覆盖检测
    ''' 获取代码覆盖报告:  python manage.py test --coverage   '''
    if COV:
        COV.stop()
        COV.save()
        print(u'报告摘要:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print(u'详细报告文件: file://%s/index.html' % covdir)
        COV.erase()
        
    
# 在请求分析监视下运行程序 【源码分析】
# 使用: python manage.py profile
@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()



# 部署命令 （每次安装或升级程序时只需要运行deploy命令）
# 使用: python  manage.py  deploy
@manager.command 
def deploy():
    ''' Run deployment tasks. '''
    from flask.ext.migrate import upgrade
    from app.models import Role, User
    
    #把数据库迁移到最新修订版本
    upgrade()
    
    #创建用户角色
    Role.insert_roles()
    
    # 让所有用户关注此用户
    User.add_self_follows()
    
    



if __name__ == '__main__':
    manager.run()