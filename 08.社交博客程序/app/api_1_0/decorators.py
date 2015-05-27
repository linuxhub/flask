#encoding:utf8

'''  修饰器 '''

from functools import wraps
from flask import g
from .errors import forbidden


# permission_required 修饰器
def permission_required(permission):
              def decorator(f):
                            @wraps(f)
                            def decorated_function(*args, **kwargs):
                                          if not g.current_user.can(permission):
                                                        return forbidden(u'没有权限')
                                          return f(*args, **kwargs)
                            return decorated_function
              return decorator
