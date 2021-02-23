'''
Created on Feb 7, 2021

@author: mballance
'''

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
                 data_width=32,
                 little_endian=True):
        self.addr_width = addr_width
        self.data_width = data_width
        self.little_endian = little_endian
        self.root = MemModel.TreeNode()
        self.n_pages = 0
        
    def write_word(self, addr, data, mask):
        """Write a data-width value to memory"""
        page = self._getpage(addr)
        pageaddr = addr & 0xFFFC
        
        for i in range(int(self.data_width/8)):
            if (mask & 1<<i) != 0:
                page.mem[pageaddr] = (data & 0xFF)
            pageaddr += 1
            data >>= 8
        
    def write32(self, addr, data, mask=0xF):
        page = self._getpage(addr)
        pageaddr = addr & 0xFFFC
        
        for i in range(4):
            if (mask & 1<<i) != 0:
                page.mem[pageaddr] = (data & 0xFF)
            pageaddr += 1
            data >>= 8
            
    def read8(self, addr) -> int:
        page = self._getpage(addr)
        pageaddr = addr & 0xFFFF

        return page.mem[pageaddr]
    
    def read16(self, addr) -> int:
        page = self._getpage(addr)
        pageaddr = addr & 0xFFFE

        data = 0        
        for i in range(2):
            if self.little_endian:
                data |= (page.mem[pageaddr] << 8*i)
            else:
                raise NotImplementedError("Big-endian read not implemented")
            pageaddr += 1
            
        return data
    
    def read32(self, addr) -> int:
        page = self._getpage(addr)
        pageaddr = addr & 0xFFFC

        data = 0        
        for i in range(4):
            if self.little_endian:
                data |= (page.mem[pageaddr] << 8*i)
            else:
                raise NotImplementedError("Big-endian read not implemented")
            pageaddr += 1
            
        return data
    
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
    
    def memset(self, addr, val, size):
        page = None

        ms_addr = addr
        for i in range(size):
            if page is None or (ms_addr & 0xFFFF) == 0:
                page = self._getpage(ms_addr)

            page.mem[ms_addr&0xFFFF] = val
            ms_addr += 1
        
    def _getpage(self, addr) -> 'MemModel.Page':
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
                    self.n_pages += 1
            node = node.nodes[ab]
            b -= 8

        return node
