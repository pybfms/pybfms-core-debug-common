'''
Created on Mar 29, 2021

@author: mballance
'''

class CallframeWindowMgr(object):
    """Manages formatting the callstack into available callframe window"""
    
    def __init__(self, 
                 window_sz, 
                 set_frame_f, 
                 clr_frame_f,
                 set_thread_f):
        self.window_sz = window_sz
        self.set_frame_f = set_frame_f
        self.clr_frame_f = clr_frame_f
        self.set_thread_f = set_thread_f
        
        self.callstack_thread = None
        self.frame_page = 0
        self.frame_start_idx = 0
        self.frame_end_idx = 0
        

    def enter(self, active_thread):
        # Update start is the starting frame (0..7) to update
        # This is relative to the displayed window
        if self.callstack_thread is active_thread:
            page = int((len(self.callstack_thread.callstack)-1)/self.window_sz)
            
            if page == self.frame_page:
                # Incremental update
                # Update the last entry in the frame
                self.frame_end_idx = len(self.callstack_thread.callstack)-1
                
                text = "%d: %s" % (self.frame_end_idx, self.callstack_thread.callstack[self.frame_end_idx].sym)
                self.set_frame_f(self.frame_end_idx%self.window_sz, text)
            else:
                # Different page
                self.frame_start_idx = self.window_sz*page
                self.frame_end_idx = len(self.callstack_thread.callstack)-1
                self.frame_page = page
                
                for i in range((self.frame_end_idx-self.frame_start_idx)+1):
                    callstack_idx = self.frame_start_idx+i
                    text = "%d: %s" % (callstack_idx, self.callstack_thread.callstack[callstack_idx].sym)
                    self.set_frame_f(i, text)
                i=self.frame_end_idx-self.frame_end_idx+1
                
                while i < self.window_sz:
                    self.clr_frame_f(i)
                    i+=1
        else:
            # Full update
            
            # Display the last stack-frame entries
            self.callstack_thread = active_thread
            page = int((len(self.callstack_thread.callstack)-1)/self.window_sz)
            self.frame_start_idx = self.window_sz*page
            self.frame_end_idx = len(self.callstack_thread.callstack)-1
            self.frame_page = page
            
            self.set_thread_f(self.callstack_thread)
                
            # Display selected entries
            for i in range((self.frame_end_idx-self.frame_start_idx)+1):
                callstack_idx = self.frame_start_idx+i
                text = "%d: %s" % (callstack_idx, self.callstack_thread.callstack[callstack_idx].sym)
                self.set_frame_f(i, text)
            i = (self.frame_end_idx-self.frame_start_idx)+1
            
            while i < self.window_sz:
                self.clr_frame_f(i)
                i+=1        
        pass
    
    def exit(self, active_thread):
        if self.callstack_thread is active_thread:
            # We're removing a single entry. 
            page = int((len(self.callstack_thread.callstack)-1)/self.window_sz)
            
            if page == self.frame_page:
                # If we're still within the current window being displayed,
                # just remove the previous entry
                self.clr_frame_f(self.frame_end_idx-self.frame_start_idx)
                self.frame_end_idx -= 1
            else:
                # We're in a different page. Update everything
                # We removed the last visible entry in the current page
                # Move back to the previous page

                self.frame_page = page                    
                self.frame_start_idx = self.window_sz*page
                self.frame_end_idx = len(self.callstack_thread.callstack)-1
                    
                for i in range((self.frame_end_idx-self.frame_start_idx)+1):
                    callstack_idx = self.frame_start_idx+i
                    text = "%d: %s" % (callstack_idx, self.callstack_thread.callstack[callstack_idx].sym)
                    self.set_frame_f(i, text)
               
                # Clear the unused entries                
                i=(self.frame_end_idx-self.frame_start_idx)+1
                while i < self.window_sz:
                    self.clr_frame_f(i)
                    i+=1
        else:
            # Full update
            self.callstack_thread = active_thread
            self.set_thread_f(self.callstack_thread)
            page = int((len(self.callstack_thread.callstack)-1)/self.window_sz)
            self.frame_page = page                    
            self.frame_start_idx = self.window_sz*page
            self.frame_end_idx = len(self.callstack_thread.callstack)-1
            
            for i in range((self.frame_end_idx-self.frame_start_idx)+1):
                callstack_idx = self.frame_start_idx+i
                text = "%d: %s" % (callstack_idx, self.callstack_thread.callstack[callstack_idx].sym)
                self.set_frame_f(i, text)
                
            i=(self.frame_end_idx-self.frame_start_idx)+1
            while i < self.window_sz:
                self.clr_frame_f(i)
                i+=1        