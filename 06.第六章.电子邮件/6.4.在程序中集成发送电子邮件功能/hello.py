#!/usr/bin/env python
#encoding:utf8
#author: linuxhub.org

from flask import  Flask, render_template, session 
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask import session
from flask import redirect, url_for 


from db_config import db
from db_config import Role,User


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'linuhub'
class NameForm(Form):
              name = StringField('What is you name? ', validators=[Required()])
              submit = SubmitField('Submit')


#发信邮箱配置信息
app.config['MAIL_SERVER'] = 'smtp.163.com'   #163邮件smtp
app.config['MAIL_PORT'] = 465                #163邮件端口
app.config['MAIL_USE_TLS'] = False           #TLS协议
app.config['MAIL_USE_SSL'] = True            #SSL协议(启用)
app.config['MAIL_USERNAME'] = 'zepingmon'    # 163邮件 用户名
app.config['MAIL_PASSWORD'] = '123456789'    # 163邮件 密码
#app.config['ADMINS'] = 'zepingmon@163.com'  # 发件人

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'                  #主题前缀
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <zepingmon@163.com>'  #发件人
app.config['FLASKY_ADMIN'] = 'root@linuxhub.org'                       #收件人


#初始化Mail对象连接smtp服务器
from flask.ext.mail import Mail
from flask.ext.mail import Message
mail = Mail(app)


#邮件
def send_email(to, subject, template, **kwargs):
              
              '''  邮件发送  '''

              # 收件人, 主题,  渲染邮件正文的模板, 关键字参数列表
              msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                            sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])

              msg.body = render_template(template + '.txt', **kwargs)    #邮件内容.主题
              msg.html = render_template(template + '.html', **kwargs)   #邮件内容.内容
              # *注: 好奇怪这body与html,邮件两个只能看到一个的内容.
              
              mail.send(msg)


@app.route('/', methods=['GET', 'POST'])
def index():
             
              form = NameForm()
              if form.validate_on_submit():
                            user = User.query.filter_by(username=form.name.data).first()
                            if user is None:   
                                          user = User(username = form.name.data)
                                          db.session.add(user)  
                                          session['known'] = False
                                          
                                          #每当表单接收新名字时,程序都会给管理员发送一封电子邮件
                                          if app.config['FLASKY_ADMIN']:
                                                        
                                                        send_email(app.config['FLASKY_ADMIN'], 'New User','mail/new_user', user=user)   
                                                        #'mail/new_user'的意思是这个目录下: templates/mail/new_user[.txt|.html] 文件
                                                                                                  
                            else:   
                                          session['known'] = True
                                          
                            session['name'] = form.name.data
                            form.name.data = ''
                            return redirect(url_for('index'))
              
              return render_template('index.html', 
                                     form = form,
                                     name = session.get('name'), 
                                     known = session.get('known', False))

if __name__ == '__main__':
              app.run(debug=True, port=80)
             