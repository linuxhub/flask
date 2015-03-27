#encoding:utf8
# pip install flask-moment

from flask import  Flask, render_template

#step 1
#获取用户电脑中的时区和区域设置模块
from flask.ext.moment import Moment
from datetime import datetime

app = Flask(__name__)

#step 2
moment = Moment(app)

@app.route('/')
def index():
	#step 3  加入一个datetime变量  
	# datetime.utcnow()  为UTC时间 
	#  datetime.now()     当前本地时间
	#return render_template('index.html', current_time=datetime.utcnow())
             	return render_template('index.html', current_time=datetime.now())

if __name__ == '__main__':
	app.run(debug=True)