#!/usr/bin/env python
#encoding:utf8
#author: linuxhub.org

from flask import  Flask, render_template, session 
from flask import session
from flask import redirect, url_for 

from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from db_config import db
from db_config import Role,User


app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'linuhub'
class NameForm(Form):
              name = StringField('What is you name? ', validators=[Required()])
              submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
              form = NameForm()
              if form.validate_on_submit():
                            user = User.query.filter_by(username=form.name.data).first()
                            if user is None:   
                                          user = User(username = form.name.data)
                                          db.session.add(user)
                                          session['known'] = False
                            else:   
                                          session['known'] = True
                                          
                            session['name'] = form.name.data
                            form.name.data = ''
                            return redirect(url_for('index'))        
              return render_template('index.html', 
                                     form = form,
                                     name = session.get('name'), 
                                     known = session.get('known', False))


from flask.ext.script import Manager, Shell #集成Python shell
manager = Manager(app)


#集成Python shell
def make_shell_contex():
              return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_contex))



if __name__ == '__main__':
              #app.run(debug=True, port=80)
              manager.run()
              
              #使用:
              # hello.py runserver --port 80
              # hello.py shell