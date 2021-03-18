'''
Created on Feb 7, 2021

@author: mballance
'''
import hvlrpc
from core_debug_common.mem_model import MemModel
from core_debug_common.params_iterator import ParamsIterator
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from hvlrpc.api_rgy import ApiRgy
from core_debug_common.method_call_data import MethodCallData
from hvlrpc.methoddef import MethodDef
from typing import List
import ctypes
from hvlrpc import va_list

class CoreDebugBfmBase(hvlrpc.Endpoint):
    
    def __init__(
            self,
            addr_width=32,
            data_width=32,
            little_endian=True):
        super().__init__()
        
        self.addr_width = addr_width
        self.data_width = data_width
        self.little_endian = little_endian
        self.mm = MemModel(addr_width, data_width, little_endian)
        self.addr2sym_m = {}
        self.sym2addr_m = {}

        # Map of addresses to methods we'll call        
        self.addr2method_m = {}
    
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
                    
    def execute(self, 
                addr : int,
                is_call : bool,
                is_ret : bool):
        """Called by the BFM specialiation to notify of an exec event"""
        
        if is_call and addr in self.addr2method_m.keys():
            # This is a method that must be reflected back to Python
            self._do_method_call(self.addr2method_m[addr])
            
        pass
    
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
        
    def get_method_params(self, m : MethodDef) -> List:
        """Called by the BFM to return a list of parameter values"""
        raise NotImplementedError("Class " + str(type(self)) + " does not implement get_method_params")
        
    def register_export_api(self, api_t):
        """Specialization of the Endpoint method"""
        super().register_export_api(api_t)
        
        apidef = ApiRgy.inst().api_bytype(api_t)
        
        # Lookup all the symbols 
        for m in apidef.methods:
            addr = self.sym2addr(m.name)
            self.addr2method_m[addr] = m
            
    def _do_method_call(self, m : MethodDef):
        p_iter = self.param_iter()
        pm = { ctypes.c_int8 : p_iter.next8, ctypes.c_uint8 : p_iter.nextu8,
            ctypes.c_int16 : p_iter.next16, ctypes.c_uint16 : p_iter.nextu16,
            ctypes.c_int32 : p_iter.next32, ctypes.c_uint32 : p_iter.nextu32,
            ctypes.c_int64 : p_iter.next64, ctypes.c_uint64 : p_iter.nextu64,
            ctypes.c_void_p : p_iter.nextptr, str : p_iter.nextstr,
            va_list : p_iter.nextva}
            
        params = []
        for p in m.params:
            if p.ptype in pm.keys():
                params.append(pm[p.ptype]())
            else:
                # Need to dig a bit more
                raise Exception("Cannot read parameter type " + str(p.ptype))
            
        mi = self.get_method_impl(m)
        
        mi(*params)
            
