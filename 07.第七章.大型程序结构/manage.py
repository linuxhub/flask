#!/usr/bin/env python
#encoding:utf8

'''  启动脚本  '''

import os
from app import create_app, db
from app.models import User, Role  #数据库模型，当前这个文件是空(2015.05.03)
from flask.ext.script import Manager, Shell  
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



#启动单元测试命令
@manager.command
def test():
    ''' Run the unit tests '''
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)



if __name__ == '__main__':
    manager.run()