#encoding:utf8
from flask import  Flask, render_template
from flask.ext.bootstrap import Bootstrap


#安装 pip install flssk-wtf
#加载 form表单
from flask.ext.wtf import Form

#加载 StringField文本字段,SubmitField提交按钮
from wtforms import StringField, SubmitField

#加载 验证函数
from wtforms.validators import Required


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
	name = None
	form = NameForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
	return render_template('index.html', form=form, name=name)

	
if __name__ == '__main__':
	app.run(debug=True)
