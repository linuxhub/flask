#encoding:utf8

# 使用HTTP内容协商处理错误 


from flask import jsonify
from app.exceptions import ValidationError
from . import api



# 400
def bad_request(message):
              response = jsonify({'error': 'bad request', 'message': message})
              response.status_code = 400
              return response

#401 认证密令不正确,服务器向客户机端返回401错误
def unauthorized(message):
              response = jsonify({'error': 'unauthorized', 'message': message})
              response.status_code = 401
              return response

# 403 Forbidden(禁止) 请求中发送的认证密令无权访问目标
def forbidden(message):
              response = jsonify({'error': 'forbidden', 'message': message})
              response.status_code = 403
              return response


# API中 ValidationError 异常的处理程序
@api.errorhandler(ValidationError)
def validation_error(e):
              return bad_request(e.args[0])

              

              