from flask import  Flask, render_template
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)

@app.route('/')
def index():
	#return '<h1> Hello Work ! </h1>'
	return render_template('index.html')

@app.route('/user/<name>')
def user(name):
	return render_template('user.html',name=name)


bootstrap = Bootstrap(app)
if __name__ == '__main__':
	app.run(debug=True)