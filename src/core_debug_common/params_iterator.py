'''
Created on Feb 21, 2021

@author: mballance
'''
import hvlrpc

class ParamsIterator(object):
    
    def __init__(self):
        super().__init__()
        pass
    
    def int8(self) -> int:
        """Returns the next 8-bit parameter"""
        raise NotImplementedError("int8 not implemented")
    
    def uint8(self) -> int:
        """Returns the next 8-bit parameter"""
        raise NotImplementedError("uint8 not implemented")
    
    def int16(self) -> int:
        """Returns the next 16-bit parameter"""
        raise NotImplementedError("int16 not implemented")
    
    def uint16(self) -> int:
        """Returns the next unsigned 16-bit parameter"""
        raise NotImplementedError("uint16 not implemented")
    
    def int32(self) -> int:
        """Returns the next 32-bit parameter"""
        raise NotImplementedError("int32 not implemented in " + str(self))
    
    def uint32(self) -> int:
        """Returns the next 32-bit parameter"""
        raise NotImplementedError("uint32 not implemented")
    
    def int64(self) -> int:
        """Returns the next 64-bit parameter"""
        raise NotImplementedError("int64 not implemented")
    
    def uint64(self) -> int:
        """Returns the next 64-bit parameter"""
        raise NotImplementedError("uint64 not implemented")
    
    def ptr(self) -> int:
        """Returns the next pointer parameter"""
        raise NotImplementedError("ptr not implemented")
    
    def str(self) -> str:
        """Returns the next string-type (const char *) parameter"""
        raise NotImplementedError("str not implemented")
    
    def va(self) -> 'ParamsIterator':
        """Returns the an iterator for variadic params"""
        raise NotImplementedError("va not implemented")
    
    