#encoding:utf8

'''  文章  '''

from flask import jsonify, request, g, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden



# 文章资源GET请求的处理程序

# 分页文章资源
@api.route('/posts/')
def get_posts():
              page = request.args.get('page', 1, type=int)
              pagination = Post.query.paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
              posts = pagination.items
              prev = None
              if pagination.has_prev:
                            prev = url_for('api.get_posts', page=page-1, _external=True)
              next = None
              if pagination.has_next:
                            next = url_for('api.get_posts', page=page+1, _external=True)
              return jsonify({
                            'posts': [post.to_json() for post in posts],
                            'prev': prev,
                            'next': next,
                            'count': pagination.total
              })



@api.route('/posts/<int:id>')
def get_post(id):
              ''' 返回单篇博客文章
                  如果在数据库中没找到指定id对应的文章,则返回404错误              
              '''
              post = Post.query.get_or_404(id)
              return jsonify(post.to_json())


# 文章资源POST请求的处理程序
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
              post = Post.from_json(request.json)
              post.author = g.current_user
              db.session.add(post)
              db.session.commit()
              # 写入数据库之后，会返回201状态码，并把Location首部的值设为刚创建的这个资源URL
              return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post', id=post.id, _external=True)}

          

# 文章资源PUT请求的处理程序
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES) #
def edit_post(id):
              post = Post.query.get_or_404(id)
              if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
                            return forbidden(u'没有权限编辑')
              post.body = request.json.get('body', post.body)
              db.session.add(post)
              return jsonify(post.to_json())




              



              