#encoding:utf8

''' 定义表单  '''
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User
from flask.ext.pagedown.fields import PageDownField #富文体编辑器


 
         
class EditProfileForm(Form):
              ''' 资料编辑表单 （普通用户） '''
              name = StringField(u'真实姓名', validators=[Length(0, 64)])
              location = StringField(u'地址', validators=[Length(0, 64)])
              about_me = TextAreaField(u'自我介绍')
              submit = SubmitField(u'确定')
              
              
class EditProfileAdminForm(Form):
              ''' 管理员使用的资料编辑表单 '''
              ''' 除去上面的3个字段外还要编辑, 用户的电子邮件,用户名,确认状态与角色   '''
              email = StringField(u'电子邮件地址', validators=[Required(), Length(1, 64), Email()])
              username = StringField(u'用户名', validators=[Required(), Length(1, 64), 
                                                               Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名只能包含字母、数字、下划线和点号.') ])
              confirmed = BooleanField(u'用户邮箱确认')
              role = SelectField('Role', coerce=int)   #下拉菜单，coerce=int意思是将值转成整数型
              name = StringField(u'真实姓名', validators=[Length(0, 64)])
              location = StringField(u'所在地', validators=[Length(0, 64)])
              about_me = TextAreaField(u'自我介绍')
              submit = SubmitField(u'确定')
              
              def __init__(self, user, *args, **kwargs):
                            '''  构造函数 '''
                            ''' 设定SelectField下拉菜单的属性choices列表的表单  '''
                            super(EditProfileAdminForm, self).__init__(*args, **kwargs)
                            self.role.choices = [(role.id, role.name)
                                                 for role in Role.query.order_by(Role.name).all()]
                            self.user = user
                            
              def validate_email(self, field):
                            if field.data != self.user.email and \
                               User.query.filter_by(email=field.data).first():
                                          raise ValidationError(u'电子邮件已经注册.')
                            
              def validate_username(self, field):
                            if field.data != self.user.username and \
                               User.query.filter_by(username=field.data).first():
                                          raise ValidationError(u'用户名已被使用.')
              

#博客文章表单
class PostForm(Form):
              #body = TextAreaField(u'你在想什么？', validators=[Required()] ) #多行文体控件
              body = PageDownField(u'你在想什么？', validators=[Required()] ) #Markdown富文本编辑器
              submit = SubmitField(u'发表')
              

#评论输入表单
class CommentForm(Form):
              body = StringField(u'输入您的评论', validators=[Required()])
              submit = SubmitField(u'发表评论')
              
              
              
