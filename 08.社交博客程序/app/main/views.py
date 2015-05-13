#encoding:utf8

'''  蓝本中定义路由程序  '''

from flask import render_template, redirect, url_for, abort, flash
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Role, User
from ..decorators import admin_required



#蓝本.路由
@main.route('/')
def index():
    return render_template('index.html')


#用户资料页面的路由
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    #如果用户不存在则返回404错误
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


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
