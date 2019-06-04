import threading
from math import ceil
from ssnmods import gvars as g
from ssnmods import (mods, queue)
from ssnmods import settings as ssn

class start_param(threading.Thread):
   
   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True


   def run(self):
      if (g.PARAMS['tab'] == "ssn"):
         g.PARAMS['num_seqs'] = mods.HandleFasta.count_fasta(g.FILES['input'])

      if (g.PARAMS['threshold'] == "ev"):
         g.PARAMS['parameter'] = "E-value"
         g.PARAMS['col'] = 2
      elif (g.PARAMS['threshold'] == "bs"):
         g.PARAMS['parameter'] = "Bitscore"
         if ((g.PARAMS['tab'] == "ssn") or (g.PARAMS['tab'] == "refine")):
            g.PARAMS['col'] = 3
         elif (g.PARAMS['tab'] == "metanodes"):
            g.PARAMS['col'] = 2

      if ((g.PARAMS['tab'] == "ssn") or (g.PARAMS['tab'] == "refine")):
         if (g.PARAMS['min'] != g.PARAMS['max']):
            even_threshold_max = ceil((g.PARAMS['max'] - g.PARAMS['min']) / g.PARAMS['step']) * g.PARAMS['step'] + g.PARAMS['min']
            if (even_threshold_max != g.PARAMS['max']):
               g.PARAMS['max'] = even_threshold_max
            g.PARAMS['num_ssn'] = (g.PARAMS['max'] - g.PARAMS['min']) / g.PARAMS['step'] + 1
         else:
            g.PARAMS['num_ssn'] = 1

      outfmt = []
      if (g.PARAMS['outfmt_cs'] == 1):
         outfmt.append("Cytoscape")
      if (g.PARAMS['outfmt_pj'] == 1):
         outfmt.append("Pajek")
      if (g.PARAMS['outfmt_gp'] == 1):
         outfmt.append("Gephi")

      g.PARAMS['format'] = ', '.join(outfmt)

      print(ssn.text['outfmt'] + g.PARAMS['format'])
      print(ssn.text['score'] + g.PARAMS['parameter'])
      if ((g.PARAMS['tab'] == "ssn") or (g.PARAMS['tab'] == "refine")):
         print(ssn.text['min'] + str(g.PARAMS['min']))
         print(ssn.text['step'] + str(g.PARAMS['step']))
         print(ssn.text['max'] + str(g.PARAMS['max']))
         print(ssn.text['num_ssn'] + str(g.PARAMS['num_ssn']))
      elif (g.PARAMS['tab'] == "metanodes"):
         print(ssn.text['meta_min'] + str(g.PARAMS['min']))
         print(ssn.text['meta_max'] + str(g.PARAMS['max']))
      elif (g.PARAMS['tab'] == "analysis"):
         print(ssn.text['meta_min'] + str(g.PARAMS['min']))  
      
      queue.pop_queue()