#!/usr/bin/env python
#encoding:utf8
#author: linuxhub.org

#encoding:utf8

#加载数据库配置脚本
from db_config import db
from db_config import Role,User


db.drop_all()  #删除数据库
db.create_all() #创建数据库

#创建表数据
#用户角色
admin_role = Role(name='Admin')
mod_role = Role(name='Moderator')
user_role = Role(name='User')

#用户名
user_john = User(username='john', role=admin_role)
user_susan = User(username='susan', role=user_role)
user_david = User(username='david', role=user_role)



if __name__ == '__main__':

              #入库前，先添加到会话中
              db.session.add(admin_role)
              db.session.add(mod_role)
              db.session.add(user_john)
              db.session.add(user_susan)
              db.session.add(user_david)

              #提交会话
              db.session.commit()

              print("\n---- 1.增加 ----")
              print("admin_role.id: %s" % admin_role.id)
              print("admin_role.id: %s" % admin_role.id)
              print("user_role.id: %s" % user_role.id)


              #修改行
              print("\n---- 2.修改 ----")
              print ("admin_role.name: %s" % admin_role.name) #查看修改前 
              admin_role.name = 'Administrator'  #修改
              db.session.add(admin_role)         #添加
              db.session.commit()                #提交
              print ("admin_role.name: %s" % admin_role.name)  #查看修改前 

              #删除行
              print("\n---- 3.删除 -----")
              print ("mod_role.name: %s" % mod_role.name) #查看删除前    
              db.session.delete(mod_role)
              db.session.commit()
              print ("mod_role.name: %s" % mod_role.name) #查看删除后
              # × 我也不知道为什么会还有，实际上已经删除了，可能是缓存 


              #查询
              print("\n---- 3.查询 -----")
              print("Role表中所有数: %s" % Role.query.all())
              print("User表中所有数: %s" % User.query.all())
              print("\nUser表中所有User角色的数据数据: %s" % User.query.filter_by(role=user_role).all())
              print("刚使用的SQL语句: %s \n" % str(User.query.filter_by(role=user_role)) )

              user_role = Role.query.filter_by(name='User').first()
              print("Role表中User的数据: %s\n" %  user_role )


              users = user_role.users  #Role表中的name列的Usero数据,与Role表中users列（关系列，其实是User表中的User列）
              print("Role表中的name列的User值对应User表中usersname列的数据: %s" % users) 
              print("第1个用户在Role表中的user数据是: %s \n" % users[0].role)  


              print user_role.users.order_by(User.username).all()
              print user_role.users.count()
              
