import threading
import dask.dataframe as dd
from ssnmods import gvars as g
from ssnmods import (mods, queue)
from ssnmods import settings as ssn

class start_sort(threading.Thread):
      
   def __init__(self):
      threading.Thread.__init__(self)
      self.daemon = True
      

   def run(self):

      df = dd.read_csv(mods.get_file("daskin_" + g.PARAMS['tab']), delimiter=";", header=None, usecols=[0,1,g.PARAMS['col']], names=["source", "target", "score"])
      df = df[df['source'] != df['target']]
      a = df.loc[:, ['source', 'target']].min(axis=1)
      b = df.loc[:, ['source', 'target']].max(axis=1)
      df['source'] = a 
      df['target'] = b

      if (g.PARAMS['threshold'] == "ev"):
         df = df.groupby(['source', 'target']).min()['score'].reset_index()
      elif (g.PARAMS['threshold'] == "bs"):
         df = df.groupby(['source', 'target']).max()['score'].reset_index()

      df.to_csv(mods.get_file("tmp"), compute=True, index=False, sep=';', header=None)

      queue.pop_queue()