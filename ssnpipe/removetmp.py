import threading
from shutil import copyfile
from ssnmods import gvars as g
from ssnmods import (mods, queue)
from ssnmods import settings as ssn

class start_clean(threading.Thread):
      
   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True
      

   def run(self):
      rmtree(mods.get_file("tmp"))
      queue.pop_queue()