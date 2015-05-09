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
                                          raise ValidationError('Email already registered.')
                            
              #验证函数2                            
              def validate_username(self, field):
                            '''  验证用户名是否已存在 '''
                            if User.query.filter_by(username=field.data).first():
                                          raise ValidationError('Username already in user.')
                           
              
              
