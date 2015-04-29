#!/usr/bin/env python
#encoding:utf8
#author: linuxhub.org

#加载数据库配置脚本
from db_config import db
from db_config import Role,User

username = 'zeping'

#查询该用户是否存在 
#没有该用户返回 None，有该用户名返回   <Role u'用户名'> 
user = User.query.filter_by(username = username ).first() 

if user is None:
               print "用户名不存在"

               print "向数据库添加用户名"
               user = User(username = username)
               db.session.add(user) #添加用户到时数据库(注: 这里没有提交)
               #db.session.commit() #提交

else:
               print "用户名存在."


#再看看用户是否存在
user = User.query.filter_by(username = username ).first()
print  user.username 


