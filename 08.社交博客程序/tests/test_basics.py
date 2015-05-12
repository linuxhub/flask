#encoding:utf8

''' 单元测试  '''

import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    
    def setUp(self):
        #''' 初始化工作  '''
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        #'''  退出清理 '''
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        # Check that the expression is false. 
        self.assertFalse(current_app is None)

        
    def test_app_is_testing(self):
        # Check that the expression is true.
        self.assertTrue(current_app.config['TESTING'])
        