#encoding:utf8

'''  检查用户权限的自宝义修饰器 '''


from functools import wraps #Python标准库中的functools包
from flask import abort
from flask.ext.login import current_user
from .models import Permission


#修饰器1
def permission_required(permission):
              '''  检查常规权限 '''
              def decorator(f):
                            @wraps(f)
                            def decorated_function(*args, **kwargs):
                                          #如果用户不指定权限则返回403错误码（同时也自定义添加一个403错误页面）
                                          if not current_user.can(permission):
                                                        abort(403)
                                          return f(*args, **kwargs)
                            return decorated_function
              return decorator



#修饰器2
def admin_required(f):
              '''  检查管理员权限 '''
              return permission_required(Permission.ADMINISTER)(f)
