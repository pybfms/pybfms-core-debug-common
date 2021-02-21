'''
Created on Feb 7, 2021

@author: mballance
'''
from aifc import data

class MemModel(object):
    
    class TreeNode(object):
        
        def __init__(self):
            self.nodes = [None]*256
            
        pass
    
    class Page(object):
        
        def __init__(self):
            self.mem = bytearray(1 << 16)
    
    def __init__(self, 
                 addr_width=32,
                 little_endian=True):
        self.addr_width = addr_width
        self.little_endian = little_endian
        self.root = MemModel.TreeNode()
        
    def write32(self, addr, data, mask=0xF):
        page = self._getpage(addr)
        pageaddr = addr & 0xFFFC
        
        for i in range(4):
            if (mask & 1<<i) != 0:
                page.mem[pageaddr] = (data & 0xFF)
            pageaddr += 1
            data >>= 8
    
    def write(self, addr, data : bytearray):

        page = self._getpage(addr)
        pageaddr = addr & 0xFFFF
        for i in range(len(data)):
            page.mem[pageaddr] = data[i]
            pageaddr += 1
            addr += 1
            
            if pageaddr > 65535:
                pageaddr = addr & 0xFFFF
                page = self._getpage(addr)

    
    def read(self, addr, nbytes : int) -> bytearray:
        ret = bytearray(bytes)
        
        page = self._getpage(addr)
        pageaddr = addr & 0xFFFF
        for i in range(nbytes):
            ret[i] = page.mem[pageaddr]
            pageaddr += 1
            addr += 1
            
            if pageaddr > 65535:
                pageaddr = addr & 0xFFFF
                page = self._getpage(addr)

        return ret
        
    def _getpage(self, addr) -> MemModel.Page:
        """Walk the tree to find the page"""
        
        node = self.root
        b = self.addr_width - 8
        
        while b > 16:
            ab = (addr >> b) & 0xFF
            if node.nodes[ab] is None:
                if b > 24:
                    node.nodes[ab] = MemModel.TreeNode()
                else:
                    node.nodes[ab] = MemModel.Page()
            node = node.nodes[ab]
            b -= 8

        return node
    
        
        