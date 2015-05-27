#encoding:utf8

# API访问认证

from flask import g, jsonify
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()





#初始化Flask-HTTPAuth
@auth.verify_password

#支持令牌的改进验证回调
def verify_password(email_or_token, password):
              ''' 如果登录密令正确,验证函数返回True 否则返回False
                  第一个认证参数可以是电子邮件或认证令牌.
                  如果这个参数为空,那就和之前一样,假定是匿名用户.
                  如果密码为空,那就假定email_or_token参数提供的是令牌,执照令牌的方式进行认证.
                  如果两个参数都不为空,假定使用常规的邮件地址和密码认证.
                  在这种实现方式中,基于令牌的认证是可可选的,由客户端决定是否使用
                  为了让视图函数难区分这两种谁方法,添加了 g.token_used 变量。
              '''              
              if email_or_token == '':
                            g.current_user = AnonymousUser()  #保存到了全局对象g中,这样视图函数便能访问
                            return True
              if password == '':
                            g.current_user = User.verify_auth_token(email_or_token)
                            g.token_used = True
                            return g.current_user is not None
              user = User.query.filter_by(email=email_or_token).first()
              if not user:
                            return False
              g.current_user = user
              g.token_used = False
              return user.verify_password(password)



# Flask-HTTPAuth 错误处理程序
@auth.error_handler
def auth_error():
              return unauthorized(u'验证出错')


#在before_request处理程序中进行认证
@api.before_request
@auth.login_required
def before_request():
              if not g.current_user.is_anonymous and not g.current_user.confirmed:
                            return forbidden(u'非法账号')              


#生成认证令牌
@api.route('/token')
def get_token():
              ''' 生成认证令牌 '''
              if g.current_user.is_anonymous() or g.token_used:
                            return unauthorized(u'证书无效')
              return jsonify({'token': g.current_user.generate_auth_token(expiration=3600),'expiration':3600}) #过期时间为1小时间


              

