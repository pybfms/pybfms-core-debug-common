'''
Created on Mar 17, 2021

@author: mballance
'''
import ctypes
from unittest.case import TestCase

from core_debug_common.params_iterator import ParamsIterator
import hvlrpc


class TestingParamsIterator(ParamsIterator):
    
    def __init__(self, tc, params):
        self.tc : TestCase = tc
        self.params_idx = 0
        self.params = params
        
    def next8(self) -> int:
        """Returns the next 8-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.tc.assertEqual(p[0], ctypes.c_int8)
        self.params_idx += 1
        return p[1]
    
    def nextu8(self) -> int:
        """Returns the next 8-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.params_idx += 1
        self.tc.assertEqual(p[0], ctypes.c_uint8)
        return p[1]
    
    def next16(self) -> int:
        """Returns the next 16-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.params_idx += 1
        self.tc.assertEqual(p[0], ctypes.c_int16)
        return p[1]
    
    def nextu16(self) -> int:
        """Returns the next 16-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.params_idx += 1
        self.tc.assertEqual(p[0], ctypes.c_uint16)
        return p[1]
    
    def next32(self) -> int:
        """Returns the next 32-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.params_idx += 1
        self.tc.assertEqual(p[0], ctypes.c_int32)
        return p[1]
    
    def nextu32(self) -> int:
        """Returns the next 32-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.params_idx += 1
        self.tc.assertEqual(p[0], ctypes.c_uint32)
        return p[1]
    
    def next64(self) -> int:
        """Returns the next 64-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.params_idx += 1
        self.tc.assertEqual(p[0], ctypes.c_int64)
        return p[1]
    
    def nextu64(self) -> int:
        """Returns the next 64-bit parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.tc.assertEqual(p[0], ctypes.c_uint64)
        self.params_idx += 1
        return p[1]
    
    def nextptr(self) -> int:
        """Returns the next pointer parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.tc.assertEqual(p[0], ctypes.c_void_p)
        self.params_idx += 1
        return p[1]
    
    def nextstr(self) -> str:
        """Returns the next string-type (const char *) parameter"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.tc.assertEqual(p[0], str)
        self.params_idx += 1
        return p[1]
    
    def nextva(self) -> 'ParamsIterator':
        """Returns the an iterator for variadic params"""
        self.tc.assertLess(self.params_idx, len(self.params))
        p = self.params[self.params_idx]
        self.tc.assertEqual(p[0], hvlrpc.va_list)
        self.params_idx += 1
        return p[1]
        