#encoding:utf8

''' auth 蓝本中的路由和视图函数  '''

from flask import  render_template
from . import auth



@auth.route('/login') # /login路由
def login():
              return render_template('auth/login.html')  
              #模板文件保存在: app/templates/auth/login.html

'''             
1. 为啥在一定要在app/templates中创建auth文件夹？

答: 因为Flask认为模板的路径是相对于程序模板文件夹而言的.
为避免与main蓝本和后续的蓝本发生模板命名冲突,
可以把蓝本使用的模板保存在单独的文件夹中.



''' 
