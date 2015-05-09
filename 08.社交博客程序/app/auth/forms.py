#encoding:utf8

'''  登录表单 '''

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email

class LoginForm(Form):
              
              #邮件使用WTForms提供的Length()和Email()验证函数              
              email = StringField(u'帐号', validators=[Required(), Length(1, 64), Email()])  #电子邮件文体字段
              
              #<input>元素
              password = PasswordField(u'密码', validators=[Required()])                  #密码字段

              #复选框              
              remember_me = BooleanField(u'记住密码')   #记住我 复选框
              
              submit = SubmitField(u'登录')  #提交按钮
              
              
