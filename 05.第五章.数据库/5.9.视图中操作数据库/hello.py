#!/usr/bin/env python
#encoding:utf8
#author: linuxhub.org

from flask import  Flask, render_template, session 
from flask.ext.bootstrap import Bootstrap

#安装 pip install flssk-wtf
#加载 form表单
from flask.ext.wtf import Form

#加载 StringField文本字段,SubmitField提交按钮
from wtforms import StringField, SubmitField

#加载 验证函数
from wtforms.validators import Required


#加载数据库配置脚本
from db_config import db
from db_config import Role,User

from flask import session   #加载session
from flask import redirect, url_for #加载重定向模块


app = Flask(__name__)
bootstrap = Bootstrap(app)


#跨站请求伪造保护 密钥
app.config['SECRET_KEY'] = 'linuhub'

#定义表单类
class NameForm(Form):
              name = StringField('What is you name? ', validators=[Required()])
              submit = SubmitField('Submit')


#路由方法
@app.route('/', methods=['GET', 'POST'])

#在视图函数中处理表单
def index():
             
              form = NameForm()
              if form.validate_on_submit():
                            
                            
                            #如果查询数据库,没有该用户名则返回None,如果用则返回用户名 <Role u'用户名'> 
                            user = User.query.filter_by(username=form.name.data).first()
                            
                            #如果用户名不存在
                            if user is None:   
                                          user = User(username = form.name.data)
                                          db.session.add(user)  #添加用户到时数据库(注: 这里没有提交)
                                          session['known'] = False
                                          
                            #用户名存在              
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
             