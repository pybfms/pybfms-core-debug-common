'''
Created on Feb 7, 2021

@author: mballance
'''
import ctypes
import pybfms
from builtins import int
from enum import IntFlag, auto
from typing import List

from core_debug_common.mem_model import MemModel
from core_debug_common.params_iterator import ParamsIterator
from core_debug_common.stack_frame import StackFrame
from core_debug_common.thread_info import ThreadInfo
from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from hvlrpc import va_list
import hvlrpc
from hvlrpc.api_rgy import ApiRgy
from hvlrpc.methoddef import MethodDef


class ExecEvent(IntFlag):
    Call = auto() # "Instruction is the first of a new function"
    Ret = auto()  # "Instruction is the first after returning from a function"
    Exc = auto()  # "Instruction is first in exception handler"

class BfmBase(hvlrpc.Endpoint):
    
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
        
        self.memwrite_cb = []

        # Callbacks activated on each instruction execution        
        self.on_exec_cb = []

        # Callbacks activated on each entry/exit        
        self.on_entry_cb = []
        self.on_exit_cb = []
        
        # Callbacks activated on specific entry/exit
        self.on_sym_entry_cb = {}
        self.on_sym_exit_cb = {}
        
        self.addr2sym_m = {}
        self.sym2addr_m = {}
        
        self.filter_m = {}

        # Create a default thread and initial stack frame
        init_t = self.create_thread("<default>")
        init_t.callstack.append(StackFrame(0, "<initial>", False))
       
        self.active_thread = init_t
        self.threads : List[ThreadInfo] = [init_t]

        # Map of addresses to methods we'll call        
        self.addr2method_m = {}
        
    def add_memwrite_cb(self, f):
        """Adds a callback function to be called on each mem write"""
        self.memwrite_cb.append(f)
        
    def del_memwrite_cb(self, f):
        """Removes an existing mem-write callback"""
        self.memwrite_cb.remove(f)
        
    def add_on_exec_cb(self, f):
        """Adds a callback invoked on each instruction executed"""
        self.on_exec_cb.append(f)
    
    def del_on_exec_cb(self, f):
        self.on_exec_cb.remove(f)
        
    def add_on_entry_cb(self, sym, f):
        """Adds a callback on a symbol or symbols"""
        if sym is None:
            self.on_entry_cb.append(f)
        else:
            addr = -1
            if isinstance(sym, str):
                if sym not in self.sym2addr_m.keys():
                    raise Exception("Symbol \"%s\" is not defined" % sym)
                else:
                    addr = self.sym2addr_m[sym]
            else:
                addr = sym
                
            def filter_cb(pc):
                if pc == addr:
                    f(pc)
            
            self.filter_m[f] = filter_cb
            self.on_entry_cb.append(filter_cb)
    
    def del_on_entry_cb(self, f):
        if f in self.filter_m.keys():
            self.on_entry_cb.remove(self.filter_m[f]) 
            self.filter_m.pop(f)
        else:
            self.on_entry_cb.remove(f)
    
    def add_on_exit_cb(self, sym, f):
        """Adds a callback on an symbol or symbols"""
        self.on_exit_cb.append(f)
    
    def del_on_exit_cb(self, f):
        self.on_exit_cb.remove(f)
    
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
                # Load all allocated sections. This will cover .bss as well
                if shdr['sh_size'] != 0 and (shdr['sh_flags'] & 0x2):
                    section = elffile.get_section(i)
                    data = section.data()
                    addr = shdr['sh_addr']
                    
                    self.mm.write(addr, data)
                    
    async def on_exec(self, sym_or_addr):
        """Waits for one or more addresses to be executed"""
        target_addr_s = set()
        if isinstance(sym_or_addr, str):
            # It's a symbol
            if sym_or_addr in self.sym2addr_m.keys():
                target_addr_s.add(self.sym2addr_m[sym_or_addr])
            else:
                raise Exception("Symbol \"" + sym_or_addr + "\" not found")
        elif isinstance(sym_or_addr, (list,tuple,set)):
            for e in sym_or_addr:
                if isinstance(e, str):
                    # It's a symbol
                    if e in self.sym2addr_m.keys():
                        target_addr_s.add(self.sym2addr_m[e])
                    else:
                        raise Exception("Symbol \"" + e + "\" not found")
                else:
                    raise Exception("address not supported")
        else:
            # It's an address
            target_addr_s.add(sym_or_addr)
            
        ev = pybfms.event()

        def waiter(pc):
            if pc in target_addr_s:
                ev.set(pc)

        self.add_on_exec_cb(waiter)

        await ev.wait()
        
        self.del_on_exec_cb(waiter)
    
        # Return the address actually hit    
        return ev.data
                    
    async def on_entry(self, sym_or_addr):
        """Waits for a function, identified by name or address, to be entered"""
        target_addr_s = set()
        if isinstance(sym_or_addr, str):
            # It's a symbol
            if sym_or_addr in self.sym2addr_m.keys():
                target_addr_s.add(self.sym2addr_m[sym_or_addr])
            else:
                raise Exception("Symbol \"" + sym_or_addr + "\" not found")
        elif isinstance(sym_or_addr, (list,tuple,set)):
            for e in sym_or_addr:
                if isinstance(e, str):
                    # It's a symbol
                    if e in self.sym2addr_m.keys():
                        target_addr_s.add(self.sym2addr_m[e])
                    else:
                        raise Exception("Symbol \"" + e + "\" not found")
                else:
                    raise Exception("address not supported")
        else:
            # It's an address
            target_addr_s.add(sym_or_addr)
            
        ev = pybfms.event()

        def waiter(pc):
            if pc in target_addr_s:
                ev.set(pc)

        self.add_on_entry_cb(None, waiter)

        await ev.wait()
        
        self.del_on_entry_cb(waiter)
    
        # Return the address actually hit    
        return ev.data        
    
    async def on_exit(self, sym_or_addr):
        target_addr_s = set()
        if isinstance(sym_or_addr, str):
            # It's a symbol
            if sym_or_addr in self.sym2addr_m.keys():
                target_addr_s.add(self.sym2addr_m[sym_or_addr])
            else:
                raise Exception("Symbol \"" + sym_or_addr + "\" not found")
        elif isinstance(sym_or_addr, (list,tuple,set)):
            for e in sym_or_addr:
                if isinstance(e, str):
                    # It's a symbol
                    if e in self.sym2addr_m.keys():
                        target_addr_s.add(self.sym2addr_m[e])
                    else:
                        raise Exception("Symbol \"" + e + "\" not found")
                else:
                    raise Exception("address not supported")
        else:
            # It's an address
            target_addr_s.add(sym_or_addr)
            
        ev = pybfms.event()

        def waiter(pc):
            if pc in target_addr_s:
                ev.set(pc)

        self.add_on_exit_cb(None, waiter)

        await ev.wait()
        
        self.del_on_exit_cb(waiter)
    
        # Return the address actually hit    
        return ev.data
    
    def create_thread(self, tid):
        """Creates a class derived from ThreadInfo"""
        # Note: should delegate to the OS-awareness class
        return ThreadInfo(tid)

    def disasm(self, addr, instr):
        raise NotImplementedError("disasm not implemented by class " + str(self))
    
    def get_sp(self) -> int:
        """Returns the current stack pointer"""
        raise NotImplementedError("get_sp not implemented by class " + str(self))
                    
    def execute(self, 
                addr    : int,
                retaddr : int,
                instr   : int,
                ev      : ExecEvent):
        """Called by the BFM specialization to notify of an exec event"""
        
        if len(self.on_exec_cb) > 0:
            for cb in self.on_exec_cb.copy():
                cb(addr, instr)

        if ev & ExecEvent.Call:
            self._do_enter(addr, retaddr)
        elif ev & ExecEvent.Ret:
            self._do_exit(addr)
        else:
            # Determine if we hit a symbol
            if addr in self.addr2sym_m.keys():
                # This is a known symbol
                pass
            pass

    def memwrite(self, waddr, wdata, wmask):
        """Called by the BFM specialiation to notify of a memory write"""
        
        # Update the mirror memory
        self.mm.write_word(waddr, wdata, wmask)
        
        # Activate any callbacks
        for cb in self.memwrite_cb.copy():
            cb(waddr, wdata, wmask)
    
    def _do_enter(self, addr, retaddr):
            
        # TODO: update callstack
        if addr in self.addr2sym_m.keys():
            sym = self.addr2sym_m[addr]
        else:
            sym = "<unknown " + hex(addr) + ">"
            
        # Record the expected return address            
        self.active_thread.callstack[-1].retaddr = retaddr

        self.active_thread.callstack.append(StackFrame(addr, sym, True))

        # Allow the specialization BFM to react
        self.enter()
        
        # Invoke all on-enter callbacks
        if len(self.on_entry_cb):
            for cb in self.on_entry_cb.copy():
                cb(addr)
            
        # Invoke any RPC methods associated with this address
        if addr in self.addr2method_m.keys():
            # This is a method that must be reflected back to Python
            self._do_method_call(self.addr2method_m[addr])
        pass
    
    def _do_exit(self, addr):
        # TODO: update callstack
        if len(self.active_thread.callstack) == 0:
            raise Exception("Attempting to return with empty callstack")
        
        
        
        if len(self.active_thread.callstack) == 0:
            raise Exception("Return results in empty callstack")
        
        frame = self.active_thread.callstack.pop()
        
        if addr != self.active_thread.callstack[-1].retaddr:
            raise Exception("Expected return address of 0x%08x ; received 0x%08x" % 
                            (self.active_thread.callstack[-1].retaddr, addr))

        # Allow the specialization BFM to react        
        self.exit(frame)
        
        # Invoke all on-exit callbacks
        if len(self.on_exit_cb):
            for cb in self.on_exit_cb.copy():
                # Pass the entry address of the function
                cb(frame.addr)
    
    def enter(self):
        """Called when a function is entered. The function will be
        top of the active thread's stack
        """
        pass
    
    def exit(self, frame : StackFrame):
        """Called after a function is exiting. This event is triggered on
        the instruction after the return completes"""
        pass
    
    def param_iter(self) -> ParamsIterator:
        """Returns a parameter iterator based on current state"""
        raise NotImplementedError("param_iter not implemented for class " + str(self))
    
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
        """Implements the mechanics of invoking an hvl-rpc method"""
        p_iter = self.param_iter()
        pm = { ctypes.c_int8 : p_iter.int8, ctypes.c_uint8 : p_iter.uint8,
            ctypes.c_int16 : p_iter.int16, ctypes.c_uint16 : p_iter.uint16,
            ctypes.c_int32 : p_iter.int32, ctypes.c_uint32 : p_iter.uint32,
            ctypes.c_int64 : p_iter.int64, ctypes.c_uint64 : p_iter.uint64,
            ctypes.c_void_p : p_iter.ptr, str : p_iter.str,
            va_list : p_iter.va}
            
        params = []
        for p in m.params:
            if p.ptype in pm.keys():
                params.append(pm[p.ptype]())
            else:
                # Need to dig a bit more
                raise Exception("Cannot read parameter type " + str(p.ptype))
            
        mi = self.get_method_impl(m)
        
        mi(*params)
            
