from Bio.SeqIO import FastaIO
from Bio import SeqIO
from ssnmods import gvars as g
from math import ceil
from glob import glob
import os
from datetime import datetime
from time import time
from itertools import (takewhile,repeat)
import re
import csv
import networkx as nx
from ssnmods import settings as ssn
from ssnmods import queue
import webbrowser


class RedirectText(object):

   def __init__(self, text_ctrl):
        self.log_box = text_ctrl
 
   def write(self, string):
      self.log_box.config(state="normal")
      self.log_box.insert("end", string)
      self.log_box.config(state="disabled")
      self.log_box.see("end")

      if (g.PARAMS['write_to_logfile'] == 1):
         g.PARAMS['write_to_logfile'] = 2
         string = self.log_box.get("1.0","end")
         with open(get_file("log"), "w") as out:
            out.write(string)
      elif (g.PARAMS['write_to_logfile'] == 2):
         with open(get_file("log"), "a") as out:
            out.write(string)
    
   def flush(self):
      pass


class RedirectError(object):
   def __init__(self):
      self.log = open(get_file("errorlog"), "a")

   def __getattr__(self, attr):
      return getattr(self.log, attr)

   def write(self, message):
      self.log.write(message)
      queue.pop_queue("error")

   def flush(self):
      pass


class HandleFasta():
   
   def count_fasta(filename):
      count = len([1 for line in open(filename) if line.startswith(">")])
      return count

   
   def is_fasta(filename):
      with open(filename, "r") as handle:
         fasta = SeqIO.parse(handle, "fasta")
         return any(fasta)


   def is_not_alignment(filename):
      for fasta in SeqIO.parse(filename, "fasta"):
         if "-" in fasta.seq:
            return False

      return True

   
   def batch_iterator(iterator, batch_size):
      entry = True   # Make sure we loop once
      while entry:
         batch = []
         while len(batch) < batch_size:
            try:
               entry = next(iterator)
            except StopIteration:
               entry = None
            if entry is None:
               # End of file
               break
            batch.append(entry)
         if batch:
            yield batch

   
   def create_newheader(outfile):
      i = 1
      with open(outfile, 'w') as out:
         for fasta in SeqIO.parse(g.FILES['input'], "fasta"):
            out.write(">" + str(i) + "\n" + str(fasta.seq) + "\n")
            i = i + 1

   
   def split_fasta(infile, num_seqs):
      split_num = ceil(num_seqs/g.PARAMS['jobs'])
      record_iter = SeqIO.parse(open(infile),"fasta")
      
      for i, batch in enumerate(HandleFasta.batch_iterator(record_iter, split_num)):
         filename = get_file("splitfasta") % (i + 1)
         with open(filename, "w") as handle:
            count = SeqIO.write(batch, handle, "fasta")

      return

   
   def list_fasta(outfile):
      filenames = glob(get_file("listfasta"))
      with open(outfile, 'w') as out:
         for file in filenames:
            out.write('"' + file + '"\n')
      return


   def create_nodetable(outfile, delim, qoutes):
      i = 1
      with open(outfile, 'w') as out:
         out.write("Id" + delim + "Label\n")
         for fasta in SeqIO.parse(g.FILES['input'], "fasta"):
            out.write(str(i) + delim + qoutes + fasta.description + qoutes + '\n')
            i = i + 1


def get_config_fields(path_filename):
   filename = os.path.basename(path_filename)
   try:
      fields = filename.rstrip().split("_")
   except IndexError:
      return False
   else:
      return fields


def resource_path(relative_path):
   try:
      base_path = sys._MEIPASS
   except Exception:
      base_path = os.path.abspath(".")

   return os.path.join(base_path, relative_path)


def time_func(what_time):
   if (what_time == 0):
      g.TIMES['current_datetime'] = datetime.now()
      g.TIMES['start'], g.TIMES['last'] = time(), time()
      return
   elif (what_time == 1):
      m, s = divmod(int(time()-g.TIMES['last']), 60)
      h, m = divmod(m, 60)
      g.TIMES['last'] = time()
   elif (what_time == 2):
      m, s = divmod(int(time()-g.TIMES['start']), 60)
      h, m = divmod(m, 60)
   return ('{:d}:{:02d}:{:02d}'.format(h, m, s))


class FormatOutput():

   def cytoscape(infile, outfile, threshold, delimin, delimout, init):
      with open(outfile, 'w') as out:
         if ((init == 0) or (init == 1)):
            out.write("Source" + delimout + "Target" + delimout + "Weight\n")
         for fn in infile:
            if (g.SSN_QUEUE[0] == "stop"):
               break
            with open(fn) as f:
               if ((init == 0) or (init == 2)):
                  next(f)
               for line in f:
                  if (g.SSN_QUEUE[0] == "stop"):
                     break
                  if (len(line.rstrip()) != 0):
                     field = line.rstrip().split(delimin)
                     if (len(field) == 3):
                        if (g.PARAMS['threshold'] == "ev"):
                           field[2] = str('{:0.2e}'.format(float(field[2])))
                        elif (g.PARAMS['threshold'] == "bs"):
                           field[2] = str(field[2])
                     if (len(field) != 3):
                        out.write(str(field[0]) + delimout + "\n")
                     elif (field[0] == "0"):
                        out.write(str(field[1]) + delimout + "\n")
                     elif (((g.PARAMS['threshold'] == "ev") and (float(field[2]) <= float("1e-" + str(threshold)))) or ((g.PARAMS['threshold'] == "bs") and (float(field[2]) >= threshold))):
                        out.write(str(field[0]) + delimout + str(field[1]) + delimout + str(field[2]) + "\n")
               
         if ((init == 1) & (g.PARAMS['tab'] == "metanodes")):
            with open(get_file("metanodes_info_cs")) as inf:
               reader = csv.reader(inf, delimiter=delimout)
               first_col = list(zip(*reader))[0]
               for row in first_col[1:]:
                  out.write(row + delimout + "\n")


   def gephi(infile, outfile, threshold, delimin, delimout, init):
      with open(outfile, 'w') as out:
         if ((init == 0) or (init == 1)):
            out.write("Source" + delimout + "Target" + delimout + "Weight\n")         
         for fn in infile:
            if (g.SSN_QUEUE[0] == "stop"):
               break
            with open(fn) as f:
               if ((init == 0) or (init == 2)):
                  next(f)
               for line in f:
                  if (g.SSN_QUEUE[0] == "stop"):
                     break
                  if (len(line.rstrip()) != 0):
                     field = line.rstrip().split(delimin)
                     if (field[0] != "0"):
                        if (g.PARAMS['threshold'] == "ev"):
                           field[2] = str('{:0.2e}'.format(float(field[2])))
                        elif (g.PARAMS['threshold'] == "bs"):
                           field[2] = str(field[2])
                        if (((g.PARAMS['threshold'] == "ev") and (float(field[2]) <= float("1e-" + str(threshold)))) or ((g.PARAMS['threshold'] == "bs") and (float(field[2]) >= threshold))):
                           out.write(str(field[0]) + delimout + str(field[1]) + delimout + str(field[2]) + "\n")

   
   def pajek(infile, outfile):
      with open(outfile, 'w') as out:
         out.write("*Vertices " + str(g.PARAMS['num_seqs']) + "\n")
         with open(get_file("nodetable_cs")) as f:
            next(f)
            for line in f:
               field = line.rstrip().split('\t')
               out.write(str(field[0]) + ' "' + str(field[1]) + '"\n')
                  
         out.write("*Edgeslist\n")
         with open(infile) as f:
            next(f)
            for line in f:
               field = line.rstrip().split('\t')
               if (len(field) == 1):
                  out.write(str(field[0]) + "\n")
               else:
                  out.write(str(field[0]) + "\t" + str(field[1]) + "\n")


def analysis_network(infile, threshold, delimiter):
   line_count = rawincount(infile, delimiter)
   print(ssn.text['analysis'] % threshold + ssn.text['edges'] % (line_count-1))
   if (line_count > ssn.settings['edge_limit']):
      return 1
   else:
      return 0


def rawincount(infile, delimiter):
   f = open(infile, 'rb')
   bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
   if (delimiter == "\t"):
      return sum( len(re.findall(b'(.*)\t(.*)\t', buf)) for buf in bufgen )
   elif (delimiter == ";"):
      return sum( len(re.findall(b'(.*);(.*);', buf)) for buf in bufgen )

def open_url(url):
    webbrowser.open_new(url)


def get_folders(tab="none"):
   folder = dict()
   if (tab == "ssn"):
      datetime_now = g.TIMES['current_datetime'].strftime("%Y%m%d_%H%M%S")
      folder['main'] = g.FOLDERS['output'] + "/" + datetime_now
   
   elif (tab == "metanodes"):
      folder['main'] = g.FOLDERS['output']
      folder['metanodes'] = folder['main'] + "/metanodes"
   
   elif (tab == "refine"):
      folder['main'] = g.FOLDERS['output']

   elif (tab == "analysis"):
      folder['main'] = g.FOLDERS['output']
      folder['analysis'] = folder['main'] + "/analysis"

   folder['tmp'] = folder['main'] + "/tmp"
   folder['networks'] = folder['main'] + "/networks"

   return folder

def get_file(filename):
   tab = g.PARAMS['tab']
   folder = get_folders(tab)

   if (filename == "log"):
      datetime_now = g.TIMES['current_datetime'].strftime("%Y%m%d_%H%M%S")
      file = folder['main'] + "/Log_" + datetime_now + ".txt"
   elif (filename == "errorlog"):
      datetime_now = g.TIMES['current_datetime'].strftime("%Y%m%d_%H%M%S")
      file = folder['main'] + "/Errors_" + datetime_now + ".txt"
   elif (filename == "blastp"):
      file = '{.}.out.txt\\\"'
   elif (filename == "masterfile"):
      file = folder['main'] + "/MASTER.txt"
   elif (filename == "fastalist"):
      file = folder['tmp'] + "/fastalist.txt"
   elif (filename == "daskin_ssn"):
      file = folder['main'] + "/MASTER.txt"
   elif (filename == "daskin_refine"):
      file = g.FILES['input']
   elif (filename == "master_in"):
      file = folder['tmp'] + "/in.*.out.txt"
   elif (filename == "tmp"):
      file = folder['tmp'] + "/tmp.*.txt"
   elif (filename == "newhead"):   
      file = folder['tmp'] + "/newhead.fasta"
   elif (filename == "nodetable_cs"):
      file = folder['main'] + "/NodeTable_cs.txt"
   elif (filename == "nodetable_gp"):
      file = folder['main'] + "/NodeTable_gp.csv"
   elif (filename == "daskin_metanodes"):
      file = folder['tmp'] + "/metanodes_tmp.txt"
   elif (filename == "metanodes"):
      file = folder['tmp'] + "/metanodes.txt"
   elif (filename == "metanodes_info_cs"):
      file = folder['metanodes'] + "/Metanodes_" + str(g.PARAMS['max']) + "_Info.txt"
   elif (filename == "metanodes_info_gp"):
      file = folder['metanodes'] + "/Metanodes_" + str(g.PARAMS['max']) + "_Info.csv"
   elif (filename == "analysis"):
      file = folder['analysis'] + "/GROUPS_" + str(g.PARAMS['min']) + "_Info.txt"
   elif (filename == "networks_pj"):
      file = folder['networks'] + "/NETWORK_pj_" + g.PARAMS['threshold'] + "_%i_.txt"
   elif (filename == "networks_cs"):
      file = folder['networks'] + "/NETWORK_cs_" + g.PARAMS['threshold'] + "_%i_.txt"
   elif (filename == "metanodes_cs"):
      file = folder['metanodes'] + "/METANODES-NETWORK_cs_" + g.PARAMS['threshold'] + "_" + str(g.PARAMS['min'])  + "_%i_.txt"
   elif (filename == "networks_gp"):
      file = folder['networks'] + "/NETWORK_gp_" + g.PARAMS['threshold'] + "_%i_.csv"
   elif (filename == "metanodes_gp"):
      file = folder['metanodes'] + "/METANODES-NETWORKS_gp_" + g.PARAMS['threshold'] + "_" + str(g.PARAMS['min'])  + "_%i_.csv"
   elif (filename == "splitfasta"):
      file = folder['tmp'] + "/in.%i.fasta"
   elif (filename == "listfasta"):
      file = folder['tmp'] + "/in.*.fasta"

   return file