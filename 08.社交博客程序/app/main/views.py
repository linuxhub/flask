#encoding:utf8

'''  蓝本中定义路由程序  '''

from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app

from . import main            #main蓝本
from .forms import NameForm   #表单
from .. import db
from ..models import User      #数据模型

from ..email import send_email  #邮件 



#蓝本.路由
@main.route('/', methods=['GET', 'POST'])

def index():
    form = NameForm()
    if form.validate_on_submit():
        
        user = User.query.filter_by(username=form.name.data).first() #数据库查询
        
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
                            
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index')) # .index 重写向在蓝本中的写法之一
        
    return render_template('index.html', 
                       form=form, 
                       name=session.get('name'),
                       known=session.get('known', False),
                       current_time=datetime.utcnow()
                       )



