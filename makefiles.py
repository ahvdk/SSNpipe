import threading
from Bio.SeqIO import FastaIO
from Bio import SeqIO
import os
from math import ceil
from shutil import copyfile
from ssnmods import gvars as g
from ssnmods import settings as ssn
from ssnmods import (mods, queue)
import sys

class start_setup(threading.Thread):

   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True

   def run(self):

      folders = mods.get_folders(g.PARAMS['tab'])

      for folder in folders:
         create_dir(folders[folder])

      if ((g.PARAMS['tab'] == "refine") or (g.PARAMS['tab'] == "metanodes")):
         new_networks_path = folders['networks'] + "/" + os.path.basename(g.FILES['input'])
         
         try:
            copyfile(g.FILES['input'], new_networks_path)
         except Exception:
            pass

      sys.stderr = mods.RedirectError()
      g.PARAMS['write_to_logfile'] = 1
      print(ssn.text['dsp'] + str(g.PARAMS['dsp']))
      print(ssn.text['input'] + g.FILES['input'])
      print(ssn.text['output'] + g.FOLDERS['output'])

      queue.pop_queue()


def create_dir(path_to):
   try: 
      os.makedirs(path_to)
   except OSError:
      if not os.path.isdir(path_to):
         raise