#encoding:utf8

'''  蓝本中定义路由程序  '''

from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from .. import db
from ..models import Role, User, Permission, Post, Comment
from ..decorators import admin_required, permission_required

from flask.ext.sqlalchemy import get_debug_queries #报告数据库的慢查询 【性能】




#蓝本.路由
#@main.route('/')
#def index():
#    return render_template('index.html')


#处理博客文章的首页路由
@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    #检查当前用户是否有写文章的权限
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    #posts = Post.query.order_by(Post.timestamp.desc()).all()    #按时间戳进行降序排序（大到小排序）
    #return render_template('index.html', form=form, posts=posts)
    
    #分页(默认20条记录 paginate()方法 配置文件FLASKY_POSTS_PER_PAGE = 20 )
    page = request.args.get('page', 1, type=int)
    
    # 显示所有博客文章 或 只显示所关注用户的博客文章 
    show_followed = False  #默认显示所有文章
    #如果cookie的show_followed字段中有值,则显示所关注用户的文章
    if current_user.is_authenticated():
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts #限制只显示所关注用户的文章
    else:
        query = Post.query  #显示所有文章
            
    #pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    #return render_template('index.html', form=form, posts=posts, pagination=pagination)
    return render_template('index.html', form=form, posts=posts, show_followed=show_followed, pagination=pagination)



#用户资料页面的路由
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    #如果用户不存在则返回404错误
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all() #获取该用户的博客文章资料页路由
    return render_template('user.html', user=user, posts=posts)


#用户员级别的资料编辑 
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form  = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash(u'您的个人资料已更新')
        return redirect(url_for('.user', username=current_user.username))
    #初始值
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me 
    return render_template('edit_profile.html', form=form)



#管理员级别的资料编辑 
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id) #如果提供有id不正确，则返回404错误
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confrmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash(u'配置文件已更新')
        return redirect(url_for('.user', username=user.username))
    #初始值
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


#博客文章的固定链接（支持评论）
@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, post=post, author=current_user._get_current_object())
        db.session.add(comment)
        flash(u'评论已发布.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    
    #page值为-1时, 会计算评论的总量和总页数,得出真正要显示的页数    
    if page == -1:
        page = (post.comments.count() -1) / current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1 
    
    #评论按照时间戳顺序排列,新评论显示在列表的底部. 
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)

       

#编辑博客文章
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    ''' 只允许博客文章作者编辑文章,但管理员例外,管理员能编辑所有用户文章.
        如果用户试图编辑其它用户的文章，视图函数会返回403错误
    '''
    
    post = Post.query.get_or_404(id)
    
    #判断如查不是文章的作者或没有管理员权限的 跳转到 403页面
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
            
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash(u'该文章已更新')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)






# 关注 用户
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    ''' 关注 用户'''
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash(u'你已经关注这个用户.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user) #调用User模型中定义的辅助方法follow()来联接两个用户.
    flash(u'已关注 %s.' % username)
    return redirect(url_for('.user', username=username))
    
       
# 取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash(u'您还没有关注这个用户.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash(u'取消关注 %s ' % username)
    return redirect(url_for('.user', username=username))



#显示用户的关注
@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title=u'的关注',
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


#显示用户的粉丝
@main.route('/followers/<username>')
def followers(username):
    ''' 关注者 (粉丝) '''
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'用户不存在')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'], error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items] #转换成一个新列表,列表中的各元素都包含user和timestamp字段.
    return render_template('followers.html', user=user, title=u'的粉丝', endpoint='.followers', pagination=pagination,
                           follows=follows)


# 所有文章 
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

# 所关注用户的文章 
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


#管理评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('get', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'], error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments, pagination=pagination, page=page)


#管理评论（启用 评论）
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


#管理评论（禁止 评论）
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate', page=request.args.get('page', 1, type=int)))


# 关闭服务器的路由 【测试】
@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


#  报告数据库的慢查询 【性能】
@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response






