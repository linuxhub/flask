#encoding:utf8

'''
    蓝本中定义错误处理程序
    自定义错误页面 
'''

from flask import render_template, request, jsonify
from . import main


#404, 客户端请求未知页面或路由时显示
@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response    
    return render_template('404.html'), 404


#500, 有未处理的异常时显示
@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response    
    return render_template('500.html'), 500


#403， HTTP禁止错误 
@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    return render_template('403.html'), 403