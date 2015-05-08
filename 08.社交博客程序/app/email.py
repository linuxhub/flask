#encoding:utf8


'''  邮件发送 '''

from threading import Thread  #多线程

from flask import current_app, render_template
from flask.ext.mail import Message
from . import mail



def send_async_email(app, msg):
              with app.app_context():
                            mail.send(msg)


def send_email(to, subject, template, **kwargs):
              
              app = current_app._get_current_object()
              
              # 收件人, 主题,  渲染邮件正文的模板, 关键字参数列表
              msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                            sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
              
              msg.body = render_template(template + '.txt', **kwargs)  #邮件内容.主题
              msg.html = render_template(template + '.html', **kwargs) #邮件内容.内容
    
              thr = Thread(target=send_async_email, args=[app, msg])
              thr.start()
           
              return thr