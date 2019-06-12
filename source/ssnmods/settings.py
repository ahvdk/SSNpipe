#TEXT VARIABLES
text = dict()

#Project text
text['name'] = "SSNpipe"
text['version'] = "v.1.0.0-beta"
text['citation'] = "Citation: Viborg, A. & Brumer, H. SSNpipe: a GUI to Simplify the Generation of Sequence Similarity Networks, to be published"

#Tooltips
tooltip = dict()

tooltip["fasta_input_tt"] = "Input file in FASTA format.\nFASTA alignments are not supported (no dashes in sequences).\nOther special characters outside of FASTA headers are not supported."
tooltip["master_input_tt"] = "File generated from a previous 'Create SSNs' session, used here as input.\nThis file will be found in the top level of the corresponding Results folder."
tooltip["metanodes_input_tt"] = "Network file generated from a previous 'Create SSNs' or 'Refine SSNs' sessions, used here as input.\nThis file will be found in 'networks' subfolder of the Results folder."
tooltip["ssn_description_tt"] = "Free text, written to log file for future reference."
tooltip["ssn_output_tt"] = "Output folder.\nIndividual network files will be written to the 'networks' subfolder in this directory.\nThe sequence ID file will be written to 'NodeTable_xx.txt'."
tooltip["refine_output_tt"] = "Output folder set by SSNpipe based on a previous 'Create SSNs' analysis.\nIndividual network files will be written to the 'networks' subfolder in this directory."
tooltip["metanodes_output_tt"] = "Output folder set by SSNpipe based on a previous 'Create SSNs' analysis.\nMetanode networks will be written to the 'metanodes' subfolder in this directory."
tooltip["analysis_output_tt"] = "Output folder set by SSNpipe based on a previous 'Create SSNs' analysis.\nGroup analysis file will be written to the 'analysis' subfolder in this directory."

tooltip["ssn_parameter_tt"] = "E-value = 1e-N\nBitscore = N\nBitscore is useful for long, highly similar sequences\nwhen E-value is below 1e-180"
tooltip["metanodes_parameter_tt"] = "This value is read from the NETWORK.txt input file selected above."

tooltip["settings_threads_tt"] = "The number of threads for parallelization of BLASTP analysis.\nThe maximum number is automatically determined from your computer’s architecture.\nSelecting the maximum number may slow performance of other processes."

tooltip["metanodes_min_tt"] = tooltip["analysis_min_tt"] = tooltip["metanodes_parameter_tt"]
tooltip["refine_description_tt"] = tooltip["analysis_description_tt"] = tooltip["metanodes_description_tt"] = tooltip["ssn_description_tt"]
tooltip["refine_parameter_tt"] = tooltip["ssn_parameter_tt"]
tooltip["analysis_input_tt"] = tooltip["metanodes_input_tt"]
tooltip["analysis_parameter_tt"] = tooltip["metanodes_parameter_tt"]


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
text['complete'] = "SSNpipe Run Complete!"
text['time_tt'] = "Total run time: %s s"
text['prgbar_error'] = "ERROR ON USER INPUT!"
text['initiating'] = "Please wait - Initiating SSNpipe"
text['critical'] = "SSNPIPE IS TRYING TO TERMINATE SAFELY - WILL QUIT ASAP - PLEASE WAIT!"
text['analysis'] = "SSN at threshold %i"
text['edges'] = " contains %i edge(s)"
text['edge_warning'] = "WARNING: Network(s) may be too large to display in Cytoscape or Gephi (>%i egdes)"
text['edge_solution'] = " - Consider creating Metanodes to reduce the number of edge(s)"
text['no_networks'] = "Unable to find previous networks!"

text['lb'] = "\n"
text['pb'] = "\n\n"

text['intro'] = text['name'] + " " + text['version'] + "\n" + text['citation']

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

#User error text

links = dict()

links['github_source'] = "https://github.com/ahvdk/SSNpipe"
links['github_wiki'] = "https://github.com/ahvdk/SSNpipe/wiki"
links['license_url'] = "http://www.gnu.org/licenses/gpl-3.0.html"
links['dep_rush_link'] = "https://github.com/shenwei356/rush"
links['dep_tk_link'] = "http://tcl.tk"
links['dep_blastp_link'] = "https://blast.ncbi.nlm.nih.gov"
links['ssnpipe_pub_link'] = "http://doi.org"
links['babbitt_pub_link'] = "http://doi.org/10.1371/journal.pone.0004345"


#SETTINGS
settings = dict()
settings['edge_limit'] = 1000000

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
            "start_clean", "run_clean", "end_clean",
            "finished"
         ]

queue['metanodes'] = [
            "intro",
            "start_setup", "run_setup", "end_setup", 
            "start_param", "run_param", "end_param", 
            "start_metanodes", "run_metanodes", "end_metanodes",
            "start_sort", "run_sort", "end_sort",
            "start_ssn", "run_ssn", "end_ssn",
            "start_clean", "run_clean", "end_clean",
            "finished"
         ]

queue['analysis'] = [
            "intro",
            "start_setup", "run_setup", "end_setup",
            "start_param", "run_param", "end_param",
            "start_metanodes", "run_metanodes", "end_metanodes",
            "start_clean", "run_clean", "end_clean",
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

btn_radio = {
   "ssn":["bs", "ev"],
   "refine":["bs", "ev"]
   }