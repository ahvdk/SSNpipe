import threading
import shlex
import subprocess
import psutil
from time import sleep
from ssnmods import gvars as g
from ssnmods import (mods, queue)
from ssnmods import settings as ssn
import platform
import sys


class start_blast(threading.Thread):
 
   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True


   def run(self):
      file_newhead = mods.get_file("newhead")
      file_fastalist = mods.get_file("fastalist")
      file_blastp = mods.get_file("blastp")    
      num_seqs = g.PARAMS['num_seqs']
      print(ssn.text['num_seqs'] + str(num_seqs))

      mods.HandleFasta.create_newheader(file_newhead)
      mods.HandleFasta.split_fasta(file_newhead, num_seqs)
      mods.HandleFasta.list_fasta(file_fastalist)

      if ((g.PARAMS['outfmt_cs'] == 1) or g.PARAMS['outfmt_pj'] == 1):
         mods.HandleFasta.create_nodetable(mods.get_file("nodetable_cs"), "\t", "")
      if (g.PARAMS['outfmt_gp'] == 1):
         mods.HandleFasta.create_nodetable(mods.get_file("nodetable_gp"), ';', '"')

      if (platform.system() == "Linux"):
         ext = ""
      elif (platform.system() == "Windows"):
         ext = ".exe"

      self.proc = subprocess.Popen(shlex.split('rush' + str(ext) + ' -i \"' + file_fastalist + '\" -j '+ str(g.PARAMS['jobs']) + ' "blastp' + ext + ' -out ' + file_blastp + ' -max_hsps 1 -max_target_seqs ' + str(num_seqs) + ' -subject \\"' + file_newhead + '\\" -evalue 0.1 -outfmt \\"6 delim=; qacc sacc evalue bitscore pident ppos length\\" -query {}"'), shell=False, stderr=sys.stderr)

      while(g.SSN_QUEUE[0] == "run_blast"):
         sleep(1)
         self.check_sub()

      if (g.SSN_QUEUE[0] == "stop"):
         self.kill(self.proc.pid)


   def check_sub(self):
      if self.proc.poll() is not None:
         queue.pop_queue()


   def kill(self, proc_pid):
      process = psutil.Process(proc_pid)
      for proc in process.children(recursive=True):
            proc.kill()
      process.kill()
      queue.pop_queue()