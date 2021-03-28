'''
Created on Mar 25, 2021

@author: mballance
'''

class StackFrame(object):
    
    def __init__(self, addr, sym, is_func=True):
        self.addr = addr
        self.retaddr = -1
        self.sym = sym
        self.is_func = is_func
        
        