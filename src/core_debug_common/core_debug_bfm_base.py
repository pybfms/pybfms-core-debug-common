'''
Created on Feb 7, 2021

@author: mballance
'''
from core_debug_common.mem_model import MemModel
from core_debug_common.params_iterator import ParamsIterator
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

class CoreDebugBfmBase(object):
    
    def __init__(
            self,
            addr_width=32,
            data_width=32,
            little_endian=True):
        self.addr_width = addr_width
        self.data_width = data_width
        self.little_endian = little_endian
        self.mm = MemModel(addr_width, data_width, little_endian)
        self.addr2sym_m = {}
        self.sym2addr_m = {}
    
    def load_elf(self, elf_path):
        """Specifies the software image running on the core being monitored"""
        
        with open(elf_path, "rb") as fp:
            elffile = ELFFile(fp)

            # Load symbols           
            symtab = elffile.get_section_by_name('.symtab')
            shstrtab = elffile.get_section_by_name('.shstrtab')
#            strtab = elffile.get_section_by_name('.strtab')
            for i in range(symtab.num_symbols()):
                sym = symtab.get_symbol(i)
                if sym.name != "":
                    self.addr2sym_m[sym["st_value"]] = sym.name
                    self.sym2addr_m[sym.name] = sym["st_value"]
                    
            # Load data to the mirror memory
            section = None
            for i in range(elffile.num_sections()):
                shdr = elffile._get_section_header(i)
                name = shstrtab.get_string(shdr['sh_name'])
                print("section: " + str(name) + " size=" + str(shdr['sh_size']) + " flags=" + hex(shdr['sh_flags']))
                # Load all allocated sections. This will cover .bss as well
                if shdr['sh_size'] != 0 and (shdr['sh_flags'] & 0x2):
                    section = elffile.get_section(i)
                    data = section.data()
                    addr = shdr['sh_addr']
                    
                    self.mm.write(addr, data)
    
    def param_iter(self) -> ParamsIterator:
        """Returns a parameter iterator based on current state"""
        raise NotImplementedError("param_iter not implemented")
    
    def sym2addr(self, sym) -> int:
        if sym in self.sym2addr_m.keys():
            return self.sym2addr_m[sym]
        else:
            raise Exception("Symbol " + sym + " not found")

    def addr2sym(self, addr) -> str:
        if addr in self.addr2sym_m.keys():
            return self.addr2sym_m[addr]
        else:
            return None
