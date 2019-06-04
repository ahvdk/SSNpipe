import threading
from ssnmods import gvars as g
from ssnmods import (mods, queue)
from ssnmods import settings as ssn
import networkx as nx

class start_metanodes(threading.Thread):
      
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
      

	def run(self):
		if (g.PARAMS['outfmt_cs'] == 1):
			delimiter = "\t"
		elif (g.PARAMS['outfmt_gp'] == 1):
			delimiter = ";"

		outfile = mods.get_file("metanodes")

		if ((g.PARAMS['tab'] == "metanodes") and (g.PARAMS['outfmt_cs'] == 1)):
			parentfile =  mods.get_file("metanodes_info_cs")
		elif ((g.PARAMS['tab'] == "metanodes") and (g.PARAMS['outfmt_gp'] == 1)):
			parentfile =  mods.get_file("metanodes_info_gp")
		elif ((g.PARAMS['tab'] == "analysis") and ((g.PARAMS['outfmt_cs'] == 1) or (g.PARAMS['outfmt_gp'] == 1))):
			parentfile = mods.get_file("analysis")

		if (g.PARAMS['outfmt_cs'] == 1):
			infile = mods.get_file("networks_cs") % int(g.PARAMS['min'])
			mods.FormatOutput.cytoscape([infile], outfile, g.PARAMS['max'], delimiter, delimiter, 2)

		if (g.PARAMS['outfmt_gp'] == 1):
			infile = mods.get_file("networks_gp") % int(g.PARAMS['min'])
			mods.FormatOutput.gephi([infile], outfile, g.PARAMS['max'], delimiter, delimiter, 2)

		meta = dict()
		H=nx.read_weighted_edgelist(outfile, delimiter=delimiter)
		connected_components = sorted(nx.connected_components(H), key = len, reverse=True)
		
		with open(parentfile, "w") as parent:
			if (g.PARAMS['tab'] == "metanodes"):
				parent.write("Metanode" + delimiter + "Size" + delimiter + "Subnodes\n")
			elif (g.PARAMS['tab'] == "analysis"):
				parent.write("Node\tSubgroup\n")
			
			i = 1
			for group in connected_components:
				group = list(group)
				if (g.PARAMS['tab'] == "metanodes"):
					parent.write(str(group[0])+ delimiter + str(len(group))+ delimiter +str(", ".join(group)) + "\n")
					for entry in group:
						meta.update({entry:group[0]})
				elif (g.PARAMS['tab'] == "analysis"):
					for entry in group:
						meta.update({entry:group[0]})
						parent.write(str(entry) + "\t" + str(i) + "\n")
					i = i + 1

		if (g.PARAMS['tab'] == "metanodes"):
			with open(mods.get_file("daskin_" + g.PARAMS['tab']), "w") as out, open(parentfile, "a") as parent:
				with open(infile) as f:
					next(f)
					for line in f:
						field = line.rstrip().split(delimiter)
						if (len(field) >= 2):
							if meta.get(field[0]) is None:
								f_zero = field[0]
							else:
								f_zero = meta.get(field[0])

							if meta.get(field[1]) is None:
								f_one = field[1]
							else:
								f_one = meta.get(field[1])
							out.write(str(f_zero) + ";" + str(f_one) + ";" + str(field[2]) + "\n")
						elif ((len(field) == 1) and (meta.get(field[0]) is None)):
							parent.write(field[0] + delimiter + "1" + delimiter + field[0] + "\n")

		if (g.PARAMS['tab'] == "analysis"):
			with open(parentfile, "a") as parent:
				with open(infile) as f:
					next(f)
					for line in f:
						field = line.rstrip().split(delimiter)
						if ((len(field) == 1) and (meta.get(field[0]) is None)):
							parent.write(field[0] + delimiter + "0\n")

		queue.pop_queue()