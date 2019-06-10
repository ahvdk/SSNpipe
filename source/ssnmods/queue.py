from ssnmods import gvars as g

def pop_queue(signal=0):
	if ((g.SSN_QUEUE[0] == "stop") or (signal == "stop")):
		g.SSN_QUEUE = ["start_clean", "run_stop", "end_stop", "terminated"]
	elif (signal == "error"):
		g.SSN_QUEUE = ["error"]
	else:
		g.SSN_QUEUE.pop(0)