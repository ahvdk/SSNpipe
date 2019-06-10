from datetime import datetime
from time import time
import sys
import psutil
from glob import glob
import copy
import os

from ssnmods import gvars as g
from ssnmods import settings as ssn
from ssnmods import (mods, queue, tooltip)

#Probably not good practice, but it works
from ssnpipe.makefiles import *
from ssnpipe.setparams import *
from ssnpipe.blast import *
from ssnpipe.makemaster import *
from ssnpipe.removeedges import *
from ssnpipe.makessn import *
from ssnpipe.removetmp import *
from ssnpipe.metanodes import *

import tkinter as tk
from tkinter import messagebox
from tkinter import StringVar
from tkinter import DoubleVar
import pygubu


class MyApplication(pygubu.TkApplication):

   def _create_ui(self):
      self.builder = builder = pygubu.Builder()
      builder.add_from_file(resource_path('gui.ui'))
      self.mainwindow = builder.get_object('mainwindow', self.master)
      self.mainmenu = menu = builder.get_object('mainmenu', self.master)
      self.set_menu(menu)
      self.abouttoplevel = self.builder.get_object('abouttoplevel', self.master)
      self.abouttoplevel.protocol("WM_DELETE_WINDOW", self.on_about_close_clicked)
      self.abouttoplevel.withdraw()
      self.inp = self.builder.get_object("ssn_input")

      builder.connect_callbacks(self)
      self.set_title(ssn.text['name'] + " " + ssn.text['version'])

      # Attach scrollbar to log_box
      self.logBox = builder.get_object('log_box', self.master)
      self.yscrollbar = builder.get_object('yscrollbar', self.master)
      self.logBox['yscrollcommand'] = self.yscrollbar.set
      self.yscrollbar['command'] = self.logBox.yview

      # Progress bar
      self.prg_lbl = tk.StringVar()
      self.builder.get_object('progress_label').config(textvariable=self.prg_lbl)
      self.prg_bar = tk.DoubleVar()
      self.builder.get_object('progress_bar').config(variable=self.prg_bar)

      # Thread settings
      self.builder.get_object('settingthreads').config(state='readonly')
      self.num_threads = tk.StringVar()
      get_threads = psutil.cpu_count(logical=True)
      self.builder.get_object('settingthreads').config(to=get_threads, textvariable=self.num_threads)
      self.num_threads.set(get_threads)

      self.builder.tkvariables["refine_input"].trace('w', self.set_refine_output)
      self.builder.tkvariables["metanodes_input"].trace('w', self.set_metanodes_output)
      self.builder.tkvariables["analysis_input"].trace('w', self.set_analysis_output)

      # Redirect stdout to log box and log file

      sys.stdout = mods.RedirectText(self.logBox)

      # Initial running parameters
      g.SSN_QUEUE = ssn.queue['initial']
      g.PARAMS['write_to_logfile'] = 0
      g.PARAMS['destroy'] = 0

      # Set tool tips
      for tip in ssn.tooltip:
         tt = self.builder.get_object(tip)
         tooltip.Tooltip(tt, text=ssn.tooltip[tip])

      # Set initiate buttons
      for btn in ssn.btn_initiate:
         btn_initiate = self.builder.get_object("btn_" + btn + "_initiate")
         btn_initiate.configure(command = lambda btn=btn: self.initiate(btn))

      # Set submit buttons
      for btn in ssn.btn_run:
         btn_run = self.builder.get_object("btn_" + btn + "_run")
         btn_run.configure(command = lambda btn=btn: self.submit(btn))

      # Change MAX scales when MIN and STEP scale change
      for tabs in ssn.scales:
         for scale in ssn.scales[tabs]:
            scale_obj = self.builder.get_object(tabs + "_threshold_" + scale)
            scale_obj.configure(command = lambda x=0, tabs=tabs: self.adjust_max_threshold(x, tabs))

      # Set radio buttons
      for tabs in ssn.btn_radio:
         for param in ssn.btn_radio[tabs]:
            scale_obj = self.builder.get_object(tabs + "_score_" + param)
            scale_obj.configure(command = lambda tabs=tabs: self.adjust_scale_thresholds(tabs))

      # Set hyperlinks
      for link in ssn.links:
         label = self.builder.get_object(link)
         label.configure(text = ssn.links[link], foreground="blue", cursor="hand2")
         label.bind("<Button-1>", lambda e, link=link: mods.open_url(ssn.links[link]))

      #Set about window
      self.builder.get_object("abouttitle").configure(text = ssn.text["name"])
      self.builder.get_object("aboutversion").configure(text = ssn.text["version"])


   def set_refine_output(self, a, b, c):
      path = self.builder.tkvariables["refine_input"].get()
      outdir = os.path.dirname(path)
      self.builder.tkvariables["refine_output_dir"].set(outdir)


   def set_metanodes_output(self, a, b, c):
      path = self.builder.tkvariables["metanodes_input"].get()
      outdir = os.path.dirname(os.path.dirname(path))
      self.builder.tkvariables["metanodes_output_dir"].set(outdir)


   def set_analysis_output(self, a, b, c):
      path = self.builder.tkvariables["analysis_input"].get()
      outdir = os.path.dirname(os.path.dirname(path))
      self.builder.tkvariables["analysis_output_dir"].set(outdir)


   def on_exit_clicked(self):
      self.quit()


   def on_new_clicked(self):
      print ("Not working yet")


   def on_about_clicked(self):
      self.abouttoplevel.deiconify()
   

   def on_about_close_clicked(self):
      self.abouttoplevel.withdraw()


   def adjust_max_threshold(self, value, tab):
      th_max = self.builder.get_object(tab + '_threshold_max')
      th_step = self.builder.get_object(tab + '_threshold_step')
      th_min = self.builder.get_object(tab + '_threshold_min')
      threshold = self.builder.tkvariables["ssn_score"].get()

      if (th_max.get() == th_min.get()):
         th_step.config(from_ = 0, to = 0)
         th_step.set(0)
      elif (th_max.get() > th_min.get()):
         if (threshold == "ev"):
            step = 20
         else:
            step = 50
         if (th_max.get()-th_min.get() <= step):
            step = th_max.get()-th_min.get()
         th_step.config(from_ = 5, to = step)
      elif (th_max.get() < th_min.get()):
         th_max.set(th_min.get())


   def adjust_scale_thresholds(self, tab):
      th_max = self.builder.get_object(tab + '_threshold_max')
      th_min = self.builder.get_object(tab + '_threshold_min')
      th_step = self.builder.get_object(tab + '_threshold_step')
      threshold = self.builder.tkvariables[tab + '_score'].get()
      if (threshold == "ev"):
         min, max, step = 130, 150, 20
      else:
         min, max, step = 750, 800, 50

      th_max.config(to = max)
      th_min.config(to = min)
      th_step.config(to = step)


   def clear_log_box(self):
      self.log_box = self.builder.get_object("log_box")
      self.log_box.config(state="normal")
      self.log_box.delete(1.0, "end")
      self.log_box.config(state="disabled")
      self.log_box.see("end")


   def process_queue(self):
      if ("end_" in g.SSN_QUEUE[0]):
         print(ssn.text['end_task'] + ssn.text['time_et'] % mods.time_func(1))
         queue.pop_queue()
         upd_bar = self.prg_bar.get()
         self.prg_bar.set(upd_bar+17)
      
      if ("start_" in g.SSN_QUEUE[0]):
         print(ssn.text['lb'] + ssn.text['date'] + datetime.now().strftime(ssn.text['dateformat']))
         print(ssn.text[g.SSN_QUEUE[0]])
         func = globals()[g.SSN_QUEUE[0]]
         func().start()
         queue.pop_queue()

      if (g.SSN_QUEUE[0] == "finished"):
         self.prg_bar.set(100)
         print(ssn.text['lb'] + ssn.text['complete'])
         print(ssn.text['time_tt'] % mods.time_func(2))
         self.prg_lbl.set(ssn.text['complete'])
         self.reset_run()
         return
      elif (g.SSN_QUEUE[0] == "terminated"):
         if (g.PARAMS['destroy'] == 1):
            root.destroy()
         else:
            self.reset_run()
            return
      elif (g.SSN_QUEUE[0] == "error"):
         print (ssn.text_err['unexpected'])
         self.reset_run()
         return
    
      self.prg_lbl.set(ssn.text['time_et'] % mods.time_func(2))
      self.master.after(1000, self.process_queue)


   def initiate(self, tab):
      g.PARAMS['state'] = "initiate"
      g.PARAMS['tab'] = tab
      
      #CHECK USER INPUT
      decision = check_user_input(g.PARAMS['state'], tab)
      self.clear_log_box()
      if (decision[0]):
         set_input_parameters(decision[1][0], decision[1][1], decision[1][2], tab)
         toggle_widgets(g.PARAMS['state'], tab)
      else:
         for error in decision[1]:
            print (error)
         self.reset_run()


   def submit(self, tab):
      g.PARAMS['tab'] = tab
      g.PARAMS['state'] = "submit"
      get_input_parameters(g.PARAMS['tab'])
      self.prg_bar.set(0)

      #CHECK USER INPUT
      decision = check_user_input(g.PARAMS['state'], tab)
      if (decision[0]):
         toggle_widgets(g.PARAMS['state'], tab)
         g.SSN_QUEUE = copy.copy(ssn.queue[tab])
         mods.time_func(0)
         self.clear_log_box()
         print(ssn.text[g.SSN_QUEUE[0]])
         queue.pop_queue()
         self.process_queue()
      
      # ERROR ON USER INPUT
      else:
         self.clear_log_box()
         for error in decision[1]:
            print (error)
         self.reset_run()


   def reset_run(self):
      toggle_widgets(g.PARAMS['state'], g.PARAMS['tab'], 1)
      sys.stderr = sys.__stderr__
      g.TIMES, g.PARAMS, g.SSN_QUEUE, g.FILES, g.FOLDERS = dict(), dict(), dict(), dict(), dict()
      g.SSN_QUEUE = ssn.queue['initial']
      g.PARAMS['write_to_logfile'] = 0
      g.PARAMS['destroy'] = 0


   def abort(self):
      toggle_widgets(g.PARAMS['state'], g.PARAMS['tab'], 2)
      if ("run_" in g.SSN_QUEUE[0]):
         print (ssn.text['abort'])
         g.SSN_QUEUE = ["stop"]
      elif ("initiate" in g.PARAMS['state']):
         self.reset_run()
      else:
         print (ssn.text['abort'])
         queue.pop_queue("stop")
 

   def abort_x(self):
      self.builder.get_object("btn_ssn_abort").config(state="disabled")
      if ((g.SSN_QUEUE[0] == "finished") or (g.SSN_QUEUE[0] == "intro") or (g.PARAMS['state'] == "initiate")):
         root.destroy()
         return
      elif ("run_" in g.SSN_QUEUE[0]):
         g.SSN_QUEUE[0] = "stop"
      else:
         queue.pop_queue("stop")

      if (g.PARAMS['destroy'] == 0):
         print (ssn.text['abort'])
         g.PARAMS['destroy'] = 1
      else:       
         print(ssn.text['critical'])
         sleep(3)
         root.destroy()


class Spinbox(ttk.Entry):

    def __init__(self, master=None, **kw):

        ttk.Entry.__init__(self, master, "ttk::spinbox", **kw)
    def set(self, value):
        self.tk.call(self._w, "set", value)


def resource_path(relative_path):
   try:
      base_path = sys._MEIPASS
   except Exception:
      base_path = os.path.abspath(".")

   return os.path.join(base_path, relative_path)


def toggle_widgets(state, tab, reset=0):
   tabs = copy.copy(ssn.tab_order)

   if (reset == 0):
      tabs.pop(tab)
      for distab in tabs:
         app.builder.get_object("mainnotebook").tab(tabs[distab], state="disabled")
      if (state == "initiate"):
         app.builder.get_object("btn_" + tab + "_abort").config(state="enabled")
         app.builder.get_object("btn_" + tab + "_run").config(state="enabled")
      elif (state == "submit"):
         app.builder.get_object("btn_" + tab + "_abort").config(state="enabled")
         app.builder.get_object("btn_" + tab + "_run").config(state="disabled")
      #app.builder.get_object(tab + "_input").config(state="disabled")
      #app.builder.get_object(tab + "_output_dir").config(state="disabled")
      #app.builder.get_object(tab + "_description").config(state="disabled")

   elif (reset == 1):
      tabs.pop(tab)
      for distab in tabs:
         app.builder.get_object("mainnotebook").tab(tabs[distab], state="normal")
      if (state == "initiate"):
         app.builder.get_object("btn_" + tab + "_abort").config(state="disabled")
         app.builder.get_object("btn_" + tab + "_run").config(state="disabled")
      elif (state == "submit"):
         if ((tab == "ssn") or (tab == "refine")):
            app.builder.get_object("btn_" + tab + "_abort").config(state="disabled")
            app.builder.get_object("btn_" + tab + "_run").config(state="enabled")
         else:
            app.builder.get_object("btn_" + tab + "_abort").config(state="disabled")
            app.builder.get_object("btn_" + tab + "_run").config(state="disabled")
            app.builder.get_object("btn_" + tab + "_initiate").config(state="enabled")

   elif (reset == 2):
      app.builder.get_object("btn_" + tab + "_abort").config(state="disabled")
      #app.builder.get_object(tab + "_input").config(state="normal")
      #app.builder.get_object(tab + "_output_dir").config(state="normal")
      #app.builder.get_object(tab + "_description").config(state="normal")


def set_input_parameters(format, score, threshold_min, tab):
   app.builder.get_object(tab + '_threshold_min').config(state="normal", from_=threshold_min, to=threshold_min)
   
   if (score == "ev"):
      app.builder.get_object(tab + '_score_ev').config(state="normal")
      app.builder.get_object(tab + '_score_ev').invoke()
      app.builder.get_object(tab + '_score_bs').config(state="disabled")
      th_max, th_step = 150, 20 
   elif (score == "bs"):
      app.builder.get_object(tab + '_score_bs').config(state="normal")
      app.builder.get_object(tab + '_score_bs').invoke()
      app.builder.get_object(tab + '_score_ev').config(state="disabled")
      th_max, th_step = 800, 50
   
   if (format == "cs"):
      app.builder.get_object(tab + '_cytoscape').config(state="normal")
      app.builder.get_object(tab + '_cytoscape').invoke()
      app.builder.get_object(tab + '_pajek').config(state="disabled")
      app.builder.get_object(tab + '_gephi').config(state="disabled")
   if (format == "pj"):
      app.builder.get_object(tab + '_pajek').config(state="normal")
      app.builder.get_object(tab + '_pajek').invoke()
      app.builder.get_object(tab + '_cytoscape').config(state="disabled")
      app.builder.get_object(tab + '_gephi').config(state="disabled")
   if (format == "gp"):
      app.builder.get_object(tab + '_gephi').config(state="normal")
      app.builder.get_object(tab + '_gephi').invoke()
      app.builder.get_object(tab + '_pajek').config(state="disabled")
      app.builder.get_object(tab + '_cytoscape').config(state="disabled")

   if ((tab == "ssn") or (tab == "refine") or (tab == "metanodes")):
      app.builder.get_object(tab + '_threshold_max').config(state="normal")
      app.builder.get_object(tab + '_threshold_max').config(from_=threshold_min+5, to=th_max)

   if ((tab == "ssn") or (tab == "refine")):
      app.builder.get_object(tab + '_threshold_step').config(state="normal")
      app.builder.get_object(tab + '_threshold_step').config(from_=5, to=th_step)


def get_input_parameters(tab):
   g.FILES['input'] = app.builder.tkvariables[tab + "_input"].get()
   g.FOLDERS['output'] = app.builder.tkvariables[tab + "_output_dir"].get()
   g.PARAMS['threshold'] = app.builder.tkvariables[tab + "_score"].get()
   g.PARAMS['dsp'] = app.builder.tkvariables[tab + "_description"].get()
   g.PARAMS['jobs'] = int(app.num_threads.get())
   g.PARAMS['min'] = app.builder.tkvariables[tab + "_threshold_min"].get()
   g.PARAMS['outfmt_cs'] = app.builder.tkvariables[tab + "_outfmt_cs"].get()
   g.PARAMS['outfmt_gp'] = app.builder.tkvariables[tab + "_outfmt_gp"].get()
   g.PARAMS['outfmt_pj'] = app.builder.tkvariables[tab + "_outfmt_pj"].get()
   g.PARAMS['step'] = 0
   g.PARAMS['max'] = g.PARAMS['min']

   if ((tab == "ssn") or (tab == "refine") or (tab == "metanodes")):
      g.PARAMS['max'] = app.builder.tkvariables[tab + "_threshold_max"].get()
   
   if ((tab == "ssn") or (tab == "refine")):
      g.PARAMS['step'] = app.builder.tkvariables[tab + "_threshold_step"].get()

   return 
 

def check_user_input(state, tab):
   result = [[],[]]
   result[0] = True
   input = app.builder.tkvariables[tab + "_input"].get()
   output = app.builder.tkvariables[tab + "_output_dir"].get()
   
   if (state == "initiate"):
      filename = os.path.basename(input)
      
      if not output:
         result[0] = False
         result[1].append(ssn.text_err['output'])

      if not input:
         result[0] = False
         result[1].append(ssn.text_err['input'])
      else:
         try:
            fields = filename.rstrip().split("_")
         except IndexError:
            result[0] = False
            result[1].append(ssn.text_err['filefmt'])
            return result
         try:
            result[1].append(fields[1])
            result[1].append(fields[2])
            result[1].append(int(fields[3]))
         except IndexError:
            result[0] = False
            result[1].append(ssn.text_err['filefmt'])
            return result
         if ((result[1][0] != "cs") and (result[1][0] != "gp")):
            result[0] = False
            result[1].append(ssn.text_err['fmtsupport'])
            return result

      return result

   elif (state == "submit"):
      cs = app.builder.tkvariables[tab + "_outfmt_cs"].get()
      gp = app.builder.tkvariables[tab + "_outfmt_gp"].get()
      pj = app.builder.tkvariables[tab + "_outfmt_pj"].get()
      if not output:
         result[0] = False
         result[1].append(ssn.text_err['output'])

      if not input:
         result[0] = False
         result[1].append(ssn.text_err['input'])
         return result
      if (tab == "ssn"):
         if not mods.HandleFasta.is_fasta(input):
            result[0] = False
            result[1].append(ssn.text_err['notfasta'])
         if not mods.HandleFasta.is_not_alignment(input):
            result[0] = False
            result[1].append(ssn.text_err['isalignment'])
      if (tab == "refine"):
         with open(input) as f:
            first_line = f.readline()
         try:
            fields = first_line.rstrip().split(";")
         except IndexError:
            result[0] = False
            result[1].append(ssn.text_err['filefmt'])
            return result
         try:
            int(fields[0])
            int(fields[1])
            int(fields[6])
         except (IndexError, ValueError) as error:
            result[0] = False
            result[1].append(ssn.text_err['filefmt'])
            return result      
      if not (cs or gp or pj):
         result[0] = False
         result[1].append(ssn.text_err['nofmt'])

      return result
   

if __name__ == '__main__':
   root = tk.Tk()
   app = MyApplication(root)  
   root.protocol("WM_DELETE_WINDOW", app.abort_x)
   root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file=resource_path('icon.gif')))
   root.mainloop()