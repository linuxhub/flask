#encoding:utf8

''' auth 蓝本中的路由和视图函数  '''

from flask import  render_template, redirect, request, url_for, flash
from . import auth
from flask.ext.login import login_user, logout_user, login_required
from ..models import User
from .forms import LoginForm


#用户登录
@auth.route('/login', methods=['GET', 'POST']) # /login路由
def login():              
              '''  用户登录  '''             
              form = LoginForm()    
              if form.validate_on_submit():
                            user = User.query.filter_by(email=form.email.data).first() 
                            
                            #如果邮件地址对应的用户存在,再调用用户对象的verify_password(密码)方法.
                            if user is not None and user.verify_password(form.password.data):
                                          
                                          #如果密码正确,则调用login_user()函数,在用户会话中把用户标记为已登录
                                          login_user(user, form.remember_me.data)
                                          
                                          return redirect(request.args.get('next') or url_for('main.index'))
                            
                            #密码不正确,提示消息
                            flash(u'用户名或密码错误.')
              
              return render_template('auth/login.html', form=form)   #模板文件保存在: app/templates/auth/login.html
              


              
#用户退出
@auth.route('/logout')
@login_required
def logout():
              ''' 用户退出 '''
              logout_user() #删除并重设用户会话
              flash(u'用户已退出') #提示消息
              return redirect(url_for('main.index')) #重定向到首页








'''             
1. 为啥在一定要在app/templates中创建auth文件夹？

答: 因为Flask认为模板的路径是相对于程序模板文件夹而言的.
为避免与main蓝本和后续的蓝本发生模板命名冲突,
可以把蓝本使用的模板保存在单独的文件夹中.

''' 


