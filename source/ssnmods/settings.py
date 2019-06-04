#TEXT VARIABLES
text = dict()

#Project text
text['name'] = "SSNpipe"
text['version'] = "build 20190603"
text['citation'] = "Citation: Viborg, A. & Brumer, H. (2019) Title, Journal, X:Y-Z"
text['subtitle'] = "A Graphical User Interface to Generate Sequence Similarity Networks"

#Tooltips
tooltip = dict()

tooltip["ssn_title_tt"] = "Create SSNs"
tooltip["refine_title_tt"] = "Refine SSNs"
tooltip["metanodes_title_tt"] = "Create Metanodes"
tooltip["analysis_title_tt"] = "Analysis SSNs"

#Pipeline execution text
text['date'] = "Date: "
text['dateformat'] = "%a, %b %d %Y, %X" #Fri, Apr 26 2019, 10:30:00
text['input'] = "Input file: "
text['num_seqs'] = "# Sequences: "
text['num_ssn'] = "# Sequence Similarity Network(s): "
text['output'] = "Output directory: "
text['outfmt'] = "Output format: "
text['dsp'] = "Description: "
text['score'] = "Score: "
text['min'] = "Threshold Min: "
text['meta_min'] = "Network Threshold: "
text['step'] = "Threshold Step: "
text['max'] = "Threshold Max: "
text['meta_max'] = "Metanode Threshold: "
text['start_metanodes'] = "Started: Creating metanodes"
text['start_setup'] = "Started: Setup files and folders"
text['start_param'] = "Started: Setup parameters"
text['start_blast'] = "Started: BLASTP all-vs-all using rush"
text['start_master'] = "Started: Creating MASTER file"
text['start_sort'] = "Started: 1. Removing Self-Loops (Self vs. Self alignments)\n2. Removing Duplicate Edges (Redudant pairwise alignments, e.g. A vs. B cf. B vs. A)"
text['start_ssn'] = "Started: Generating SSN(s)"
text['start_clean'] = "Started: Deleting tmp folder and files"
text['end_task'] = "Finished"
text['time_et'] = " - Elapsed time: %s s"
text['abort'] = "RUN ABORTED BY USER - THIS JOB IS UNFINISHED!"
text['complete'] = "SSNPipe Run Complete!"
text['time_tt'] = "Total run time: %s s"
text['prgbar_error'] = "ERROR ON USER INPUT!"
text['initiating'] = "Please wait - Initiating SSNPipe"
text['critical'] = "SSNPIPE IS TRYING TO TERMINATE SAFELY - WILL QUIT ASAP - PLEASE WAIT!"
text['analysis'] = "SSN at threshold %i"
text['edges'] = " contains %i edge(s)"
text['edge_warning'] = "WARNING: Network(s) may be too large to display in Cytoscape or Gephi (>%i egdes)"
text['edge_solution'] = " - Consider creating Metanodes to reduce the number of edge(s)"
text['no_networks'] = "Unable to find previous networks!"

text['lb'] = "\n"
text['pb'] = "\n\n"

text['intro'] = text['name'] + " " + text['version'] + "\n" + text['subtitle'] + "\n" + text['citation']

#User error text

text_err = dict()

text_err['output'] = "No results folder specified"
text_err['input'] = "No input file specified"
text_err['filefmt'] = "Unrecognized input fileformat"
text_err['notfasta'] = "Input file not recognized as FASTA"
text_err['fmtsupport'] = "This feature is (for now) only supported for Cytoscape (cs) and Gephi (gp) format"
text_err['nofmt'] = "No output format specified"
text_err['isalignment'] = "FASTA alignment files are not supported (one or more of your sequences contains a hyphen (-)"
text_err['unexpected'] = "\n\n\nUNEXPETCED ERROR, PLEASE SEND LOG AND ERROR FILES TO\nssnpipe@ahv.dk"

#SETTINGS
settings = dict()
settings['edge_limit'] = 30

###
#DO NOT CHANGE THE BELOW SETTINGS UNLESS YOU KNOW WHAT YOU ARE DOING!
###

#QUEUES
queue = dict()

queue['initial'] = [
			"intro", 
			"finished"
			]

queue['ssn'] = [
            "intro",
            "start_setup", "run_setup", "end_setup", 
            "start_param", "run_param", "end_param", 
            "start_blast", "run_blast", "end_blast",
            "start_master", "run_master", "end_master",
            "start_sort", "run_sort", "end_sort",
            "start_ssn", "run_ssn", "end_ssn",
            "start_clean", "run_clean", "end_clean",
            "finished"
         ]

queue['refine'] = [
            "intro",
            "start_setup", "run_setup", "end_setup", 
            "start_param", "run_param", "end_param",
            "start_sort", "run_sort", "end_sort", 
            "start_ssn", "run_ssn", "end_ssn",
            "finished"
         ]

queue['metanodes'] = [
            "intro",
            "start_setup", "run_setup", "end_setup", 
            "start_param", "run_param", "end_param", 
            "start_metanodes", "run_metanodes", "end_metanodes",
            "start_sort", "run_sort", "end_sort",
            "start_ssn", "run_ssn", "end_ssn",
            "finished"
         ]

queue['analysis'] = [
            "intro",
            "start_setup", "run_setup", "end_setup",
            "start_param", "run_param", "end_param",
            "start_metanodes", "run_metanodes", "end_metanodes",
            "finished"
         ]

#MISC
tab_order = {
   "ssn":0,
   "refine":1,
   "metanodes":2,
   "analysis":3
   }

btn_initiate = [
   "metanodes",
   "analysis",
   ]

btn_run = [
   "ssn",
   "refine",
   "metanodes",
   "analysis"
   ]

tooltips = [
	"ssn_title_tt",
	"metanodes_title_tt",
	"refine_title_tt",
	"analysis_title_tt"
	]

scales = {
   "ssn":["min", "step", "max"],
   "refine":["min", "step", "max"]
   }