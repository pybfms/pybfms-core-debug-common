'''
Created on Mar 25, 2021

@author: mballance
'''
from core_debug_common.stack_frame import StackFrame
from typing import List

class ThreadInfo(object):
    """Holds data about the state of a thread"""
    
    def __init__(self, tid):
        self.tid = tid
        self.stack_base = -1
        self.callstack : List[StackFrame] = []
