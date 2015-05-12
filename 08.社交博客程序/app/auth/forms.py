#encoding:utf8

'''  登录表单 '''

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
              ''' 用户登录  '''
              
              #邮件使用WTForms提供的Length()和Email()验证函数              
              email = StringField(u'帐号', validators=[Required(), Length(1, 64), Email()])  #电子邮件文体字段
              
              #<input>元素
              password = PasswordField(u'密码', validators=[Required()])                  #密码字段

              #复选框              
              remember_me = BooleanField(u'记住密码')   #记住我 复选框
              
              submit = SubmitField(u'登录')  #提交按钮
              

class RegistrationForm(Form):
              ''' 用户注册 '''
              
              email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
              
              #用户名只能包含字母、数字、下划线和点号
              username = StringField(u'用户名', validators=[Required(), Length(1, 64), 
                                                               Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名只能包含字母、数字、下划线和点号.') ])
              
              password = PasswordField(u'密码', validators=[Required(), EqualTo('password2', message=u'两次输入的密码不正确.')])
              
              password2 = PasswordField(u'确认密码', validators=[Required()])
              
              submit = SubmitField(u'注册')
              
              #验证函数1
              def validate_email(self, field):
                            '''  验证邮件是否已注册  '''
                            if User.query.filter_by(email=field.data).first():
                                          raise ValidationError(u'邮箱已注册.')
                            
              #验证函数2                            
              def validate_username(self, field):
                            '''  验证用户名是否已存在 '''
                            if User.query.filter_by(username=field.data).first():
                                          raise ValidationError(u'用户名已存在.')
                           
#修改密码
class ChangePasswordForm(Form):
              '''  修改密码 ''' 
              old_password = PasswordField(u'原密码', validators=[Required()])
              password = PasswordField(u'新密码', validators=[Required(), EqualTo('password2', message=u'您两次输入的新密码不一致')])
              password2 = PasswordField(u'重输密码',validators=[Required()])
              submit = SubmitField(u'更新密码')
              
              

#重置密码              
class PasswordResetRequestForm(Form):
              '''  重置密码请求 '''
              email = StringField(u'邮件地址', validators=[Required(),Length(1, 64),Email()] )
              submit = SubmitField(u'重置密码')


class PasswordResetForm(Form):
              '''  重置密码  '''
              email = StringField(u'账号', validators=[Required(), Length(1, 64), Email()] )
              password = PasswordField(u'新密码', validators=[Required(), EqualTo('password2', message=u'您两次输入的新密码不一致') ])
              password2 = PasswordField(u'重输密码', validators=[Required()])
              submit = SubmitField(u'重置密码')
              
              def validate_email(self, field):
                            if User.query.filter_by(email=field.data).first() is None:
                                          raise ValidationError(u'您输入的账号(邮件地址)不存在.')
              
              

#修改邮件地址
class ChangeEmailForm(Form):
              '''  修改邮件地址 '''
              email = StringField(u'新邮件地址', validators=[Required(), Length(1, 64), Email()])
              password = PasswordField(u'密码', validators=[Required()])
              submit = SubmitField(u'更改邮件地址')
              
              def validate_email(self, field):
                            if User.query.filter_by(email=field.data).first():
                                          raise ValidationError(u'该邮件地址已注册')
              
              
