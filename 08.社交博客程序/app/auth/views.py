#encoding:utf8

''' auth 蓝本中的路由和视图函数  '''

from flask import  render_template, redirect, request, url_for, flash
from . import auth
from flask.ext.login import login_user, logout_user, login_required, current_user
from ..models import User
from .. import db
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


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
              ''' 用户注册 '''
              form = RegistrationForm()
              if form.validate_on_submit():
                            user = User(email=form.email.data,
                                        username=form.username.data,
                                        password=form.password.data)
                            db.session.add(user)
                            db.session.commit() #因为确认用户需要id值,所以提交
                            token = user.generate_confirmation_token() #生成令牌
                            send_email(user.email, u'确认您的帐户',
                                       'auth/email/confirm', user=user, token=token)
                            flash(u'验证邮件已发送,请登录邮箱进行确认!')
                            return redirect(url_for('main.index'))
              return render_template('auth/register.html', form=form)
                            

#确认用户的视图函数
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
              '''  确认用户  '''
              
              #如果已登录的用户,已确认过验证,则重定向到首页
              if current_user.confirmed:
                            return redirect(url_for('main.index'))
              
              if current_user.confirm(token):
                            flash(u'帐号已验证!') #用户登录后的提示
              #发现个问题： 如果用户没登录验证了链接会由python中的flask_login包发现提示“Please log in to access this page.”
              #flask/venv/lib/python2.7/site-packages/flask_login.py:
              #LOGIN_MESSAGE = u'Please log in to access this page.'
              #我想这个消息应该可以自己定义
                            
              else:
                            flash(u'确认链接无效或已过期.') #用户登录后的提示

              return redirect(url_for('main.index'))



#处理程序中过滤未确认的帐户
@auth.before_app_request
def before_request():
              ''' 1.处理程序中过滤未确认的帐户  '''
              ''' 2.更新已登录用户的访问时间 '''
              if current_user.is_authenticated():
                            current_user.ping()   #更新已登录用户的访问时间
                            if not current_user.confirmed \
                               and request.endpoint[:5] != 'auth.' \
                               and request.endpoint != 'static':
                                          return redirect(url_for('auth.unconfirmed'))
              
@auth.route('/unconfirmed')
def unconfirmed():
              if current_user.is_anonymous() or current_user.confirmed:
                            return redirect(url_for('main.index'))
              return render_template('auth/unconfirmed.html')



#重新发送帐户确认邮件
@auth.route('/confirm')
@login_required
def resend_confirmation():
              token = current_user.generate_confirmation_token()
              send_email(current_user.email, u'确认您的帐户', 'auth/email/confirm', user=current_user, token=token)
              flash(u'一个新的确认邮件,已经发送到您邮箱.')
              return redirect(url_for('main.index'))


#更改密码
@auth.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
              form = ChangePasswordForm()
              if form.validate_on_submit():                          

                            #判断原始密码是否正确(如果正确赋值)
                            if current_user.verify_password(form.old_password.data):  
                                          current_user.password = form.password.data
                                          db.session.add(current_user)
                                          flash(u'密码已更改.')
                                          return redirect( url_for('main.index') )
                            else:
                                          flash(u'原始密码错误')
              return render_template("auth/change_password.html", form=form)


#重置密码
@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
              
              ''' 重置密码 (用户请求重置密码)  '''
              
              #如果用户没有登录就跳转到首页
              if not current_user.is_anonymous():
                            return redirect(url_for('main.index'))
              
              form = PasswordResetRequestForm()
              if form.validate_on_submit():
                            user = User.query.filter_by(email=form.email.data).first()
                            if user:
                                          token = user.generate_reset_token()
                                          send_email(user.email, u'重置密码', 'auth/email/reset_password', user=user, token=token, next=request.args.get('next'))
                                          #内容文件在: app/templates/auth/email/reset_password[.html|.txt] 
                                           
                                          flash(u'重置密码邮件已发送到您邮箱,请查收！')
                            return redirect(url_for('auth.login'))
              return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):              
              ''' 重置密码  '''
              if not current_user.is_anonymous():
                            return redirect(url_for('main.index'))
              form = PasswordResetForm()
              if form.validate_on_submit():
                            user = User.query.filter_by(email=form.email.data).first()
                            #如查用户不存在则跳转到首页                            
                            if user is None:
                                          return redirect(url_for('main.index'))
                            if user.reset_password(token, form.password.data):
                                          flash(u'密码已更新')
                                          return redirect(url_for('auth.login'))
                            else:
                                          return redirect(url_for('main.index'))
              return render_template('auth/reset_password.html', form=form)


#更改邮件地址
@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
              ''' 更改邮件地址 '''
              form = ChangeEmailForm()
              if form.validate_on_submit():
                            if current_user.verify_password(form.password.data):
                                          new_email = form.email.data
                                          token = current_user.generate_email_change_token(new_email)
                                          send_email(new_email, u'确认您的邮件地址', 'auth/email/change_email', user=current_user, token=token)
                                          flash(u'邮件已发送,请到新邮件地址查收！')
                                          return redirect(url_for('main.index'))
                            else:
                                          flash(u'密码错误')
              return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
              ''' 验证 更改邮件地址 '''
              if current_user.change_email(token):
                            flash(u'您的电子邮件地址已更改')
              else:
                            flash(u'链接无效或已过期')
              return redirect(url_for('main.index'))
                            
                                          
              

    
              