import threading
from glob import glob
from Bio.SeqIO import FastaIO
from Bio import SeqIO
from ssnmods import gvars as g
from ssnmods import (mods, queue)
from ssnmods import settings as ssn
from glob import glob

class start_ssn(threading.Thread):
      
   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True
   

   def run(self):
      warning = 0
      infile = glob(mods.get_file("tmp"))
      
      if ((g.PARAMS['outfmt_pj'] == 1) or (g.PARAMS['outfmt_cs'] == 1)):
         if ((g.PARAMS['tab'] == "ssn") or (g.PARAMS['tab'] == "refine")):
            outfile = mods.get_file("networks_cs") % int(g.PARAMS['min'])
         elif (g.PARAMS['tab'] == "metanodes"):
            outfile = mods.get_file("metanodes_cs") % int(g.PARAMS['max'])
         mods.FormatOutput.cytoscape(infile, outfile, g.PARAMS['min'], ";", "\t", 1)
         warning = warning + mods.analysis_network(outfile, g.PARAMS['min'], "\t")

      if (g.PARAMS['outfmt_gp'] == 1):
         if ((g.PARAMS['tab'] == "ssn") or (g.PARAMS['tab'] == "refine")):
            outfile = mods.get_file("networks_gp") % int(g.PARAMS['min'])
         elif (g.PARAMS['tab'] == "metanodes"):
            outfile = mods.get_file("metanodes_gp") % int(g.PARAMS['max'])
         mods.FormatOutput.gephi(infile, outfile, g.PARAMS['min'], ";", ";", 1)
         warning = warning + mods.analysis_network(outfile, g.PARAMS['min'], ";")

      if (g.PARAMS['outfmt_pj'] == 1):
         outfile = mods.get_file("networks_pj") % int(g.PARAMS['min'])
         infile = mods.get_file("networks_cs") % int(g.PARAMS['min'])
         mods.FormatOutput.pajek(infile, outfile)

      if (g.PARAMS['step'] != 0):
         for i in range(g.PARAMS['min'] + g.PARAMS['step'], g.PARAMS['max'] + g.PARAMS['step'], g.PARAMS['step']):
            if (g.SSN_QUEUE[0] == "stop"):
               break
            if ((g.PARAMS['outfmt_pj'] == 1) or (g.PARAMS['outfmt_cs'] == 1)):
               infile = [mods.get_file("networks_cs") % int(i-g.PARAMS['step'])]
               outfile = mods.get_file("networks_cs") % int(i)
               mods.FormatOutput.cytoscape(infile, outfile, i, "\t", "\t", 0)
               warning = warning + mods.analysis_network(outfile, i, "\t")

            if (g.PARAMS['outfmt_gp'] == 1):
               infile = [mods.get_file("networks_gp") % int(i-g.PARAMS['step'])]
               outfile = mods.get_file("networks_gp") % int(i)
               mods.FormatOutput.gephi(infile, outfile, i, ";", ";", 0)
               warning = warning + mods.analysis_network(outfile, i, ";")

            if (g.PARAMS['outfmt_pj'] == 1):
               infile = mods.get_file("networks_cs") % int(i)
               outfile = mods.get_file("networks_pj") % int(i)
               mods.FormatOutput.pajek(infile, outfile)

      if (warning >= 1):
         print(ssn.text['edge_warning'] % ssn.settings['edge_limit'] + ssn.text['edge_solution'])

      queue.pop_queue()

      return