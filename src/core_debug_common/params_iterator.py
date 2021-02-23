'''
Created on Feb 21, 2021

@author: mballance
'''

class ParamsIterator(object):
    
    def __init__(self):
        pass
    
    def next8(self) -> int:
        """Returns the next 8-bit parameter"""
        raise NotImplementedError("next8 not implemented")
    
    def nextu8(self) -> int:
        """Returns the next 8-bit parameter"""
        raise NotImplementedError("next8 not implemented")
    
    def next16(self) -> int:
        """Returns the next 16-bit parameter"""
        raise NotImplementedError("next8 not implemented")
    
    def nextu16(self) -> int:
        """Returns the next 16-bit parameter"""
        raise NotImplementedError("next8 not implemented")
    
    def next32(self) -> int:
        """Returns the next 32-bit parameter"""
        raise NotImplementedError("next32 not implemented")
    
    def nextu32(self) -> int:
        """Returns the next 32-bit parameter"""
        raise NotImplementedError("next32 not implemented")
    
    def next64(self) -> int:
        """Returns the next 64-bit parameter"""
        raise NotImplementedError("next64 not implemented")
    
    def nextu64(self) -> int:
        """Returns the next 64-bit parameter"""
        raise NotImplementedError("next64 not implemented")
    
    def nextptr(self) -> int:
        """Returns the next pointer parameter"""
        raise NotImplementedError("nextptr not implemented")
    
    def nextstr(self) -> str:
        """Returns the next string-type (const char *) parameter"""
        raise NotImplementedError("nextstr not implemented")
    
    def nextva(self) -> 'ParamsIterator':
        """Returns the an iterator for variadic params"""
        raise NotImplementedError("nextva not implemented")
    
    