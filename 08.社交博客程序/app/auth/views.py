#encoding:utf8

''' auth 蓝本中的路由和视图函数  '''

from flask import  render_template, redirect, request, url_for, flash
from . import auth
from flask.ext.login import login_user, logout_user, login_required, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm #表单类
from .. import db


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



#用户注册
@auth.route('register', methods=['GET', 'POST'])
def register():
              form = RegistrationForm()
              if form.validate_on_submit():
                            user = User(email=form.email.data,
                                        username=form.username.data,
                                        password=form.password.data)
                            db.session.add(user)
                            flash(u'注册成功!  现在,您可以登录了.')
                            return redirect(url_for('auth.login'))
              return render_template('auth/register.html', form=form)
                            