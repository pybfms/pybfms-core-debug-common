'''
Created on Mar 17, 2021

@author: mballance
'''
import ctypes

from core_debug_common.core_debug_bfm_base import CoreDebugBfmBase, ExecEvent
from core_debug_common_test_case import CoreDebugCommonTestCase
from hvlrpc import va_list
import hvlrpc
from testing_params_iterator import TestingParamsIterator


class TestMethodCall(CoreDebugCommonTestCase):
    
    def test_smoke(self):
        class TestBfm(CoreDebugBfmBase):
            
            def __init__(self):
                super().__init__()
                self.paramlists = []
                self.paramlist_idx = 0
                
            def param_iter(self):
                ret = self.paramlists[self.paramlist_idx]
                self.paramlist_idx += 1
                return ret

        @hvlrpc.api_exp
        class my_api(object):
            
            @hvlrpc.func
            def my_method(self, a : ctypes.c_uint32):
                print("my_method: " + str(a))
                
        bfm = TestBfm()
        bfm.paramlists.append(TestingParamsIterator(self,
            [
                (ctypes.c_uint32, 5)
            ]))
        
        bfm.sym2addr_m["my_method"] = 20
        
        bfm.register_export_api(my_api)
        
        bfm.execute(20, True, False)
        
    def test_va1(self):
        class TestBfm(CoreDebugBfmBase):
            
            def __init__(self):
                super().__init__()
                self.paramlists = []
                self.paramlist_idx = 0
                
            def param_iter(self):
                ret = self.paramlists[self.paramlist_idx]
                self.paramlist_idx += 1
                return ret

        @hvlrpc.api_exp
        class my_api(object):
            
            @hvlrpc.func
            def my_method(self, a : ctypes.c_uint32, ap : va_list):
                print("my_method: " + str(a) + " " + str(ap.nextstr()))
                
        bfm = TestBfm()
        bfm.paramlists.append(TestingParamsIterator(self,
            [
                (ctypes.c_uint32, 5),
                (va_list, TestingParamsIterator(self,[
                    (str, "Hello")
                    ]))
            ]))
        
        bfm.sym2addr_m["my_method"] = 20
        
        bfm.register_export_api(my_api)
        
        bfm.execute(20, ExecEvent.Call)

    def test_two_call(self):
        class TestBfm(CoreDebugBfmBase):
            
            def __init__(self):
                super().__init__()
                self.paramlists = []
                self.paramlist_idx = 0
                
            def param_iter(self):
                ret = self.paramlists[self.paramlist_idx]
                self.paramlist_idx += 1
                return ret

        @hvlrpc.api_exp
        class my_api(object):
            
            @hvlrpc.func
            def my_m1(self, a : ctypes.c_uint32, ap : va_list):
                print("my_m1: " + str(a) + " " + str(ap.nextstr()))
                
            @hvlrpc.func
            def my_m2(self, a : ctypes.c_uint32, b : ctypes.c_uint32):
                print("my_m2: " + str(a) + " " + str(b))
                
        bfm = TestBfm()
        bfm.paramlists.append(TestingParamsIterator(self,
            [
                (ctypes.c_uint32, 5),
                (va_list, TestingParamsIterator(self,[
                    (str, "Hello")
                    ]))
            ]))
        bfm.paramlists.append(TestingParamsIterator(self,
            [
                (ctypes.c_uint32, 6),
                (ctypes.c_uint32, 7),
            ]))
        
        bfm.sym2addr_m["my_m1"] = 20
        bfm.sym2addr_m["my_m2"] = 40
        
        bfm.register_export_api(my_api)
       
        bfm.execute(20, ExecEvent.Call)
        bfm.execute(40, ExecEvent.Call)
        
        