'''
Created on Feb 21, 2021

@author: mballance
'''
from unittest.case import TestCase
from core_debug_common.mem_model import MemModel

class TestMemModel(TestCase):
    
    def test_smoke(self):
        mm = MemModel()
        
        mm.write(0x00000000, [1, 2, 3, 4])
        mm.write(0x80000000, [5, 6, 7, 8])
        
        val = mm.read32(0x00000000)
        self.assertEqual(val, 0x04030201)
        
        val = mm.read32(0x80000000)
        self.assertEqual(val, 0x08070605)
        
        self.assertEqual(mm.n_pages, 2)