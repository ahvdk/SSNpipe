import threading
import dask.dataframe as dd
from ssnmods import gvars as g
from ssnmods import (mods, queue)
from ssnmods import settings as ssn
from glob import glob
from Bio.SeqIO import FastaIO
from Bio import SeqIO

class start_master(threading.Thread):
      
   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True
      

   def run(self):

      filenames = glob(mods.get_file("master_in"))
      with open(mods.get_file("masterfile"), 'w') as out:
         for fastaheader in SeqIO.parse(mods.get_file("newhead"), "fasta"):
            out.write(fastaheader.description + ";0;0;0;0;0;0\n")
         for fn in filenames:
            if (g.SSN_QUEUE[0] == "stop"):
               break
            with open(fn) as f:
               for line in f:
                  if (len(line.rstrip()) != 0):
                     out.write(line)

      queue.pop_queue()

      return