'''
Created on Mar 17, 2021

@author: mballance
'''
from unittest.case import TestCase
import hvlrpc

class CoreDebugCommonTestCase(TestCase):
    
    def setUp(self):
        hvlrpc.test_init()
        
    def tearDown(self):
        hvlrpc.test_init()