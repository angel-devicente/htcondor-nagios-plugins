#!/usr/bin/python

import sys
import configparser
import htcondor

# magic numbers:
# https://htcondor-wiki.cs.wisc.edu/index.cgi/wiki?p=MagicNumbers

try:
	configfile=sys.argv[1]
	conf=configparser.ConfigParser()
	conf.read(configfile)
	print conf.sections()
except:
	pass

#collector = htcondor.Collector('ci.kbase.us:9618')
collector = htcondor.Collector()

collectors = collector.query(htcondor.AdTypes.Collector, "true", ["Name"])
numCollectors = len(collectors)
negotiators = collector.query(htcondor.AdTypes.Negotiator, "true", ["Name"])
numNegotiators = len(negotiators)

collectorState=3
collectorStateText='UNKNOWN'
negotiatorState=3
negotiatorStateText='UNKNOWN'

if (numCollectors < 1):
	collectorState=2
	collectorStateText='CRITICAL'
if (numCollectors > 0):
	collectorState=0
	collectorStateText='OK'
print str(collectorState) + ' Condor_num_collectors collectors=' + str(numCollectors) + ' ' + collectorStateText + ' - ' + str(numCollectors) + ' collectors running'

if (numNegotiators < 1):
	negotiatorState=2
	negotiatorStateText='CRITICAL'
if (numNegotiators > 0):
	negotiatorState=0
	negotiatorStateText='OK'
print str(negotiatorState) + ' Condor_num_negotiators negotiators=' + str(numNegotiators) + ' ' + negotiatorStateText + ' - ' + str(numNegotiators) + ' negotiators running'

slots = collector.query(htcondor.AdTypes.Startd, "true")

jobCounts = {
	'njs': 0,
	'bigmemlong': 0,
	'bigmem': 0,
	'kb_upload': 0
}
slotCounts = {
	'njs': 0,
	'bigmemlong': 0,
	'bigmem': 0,
	'kb_upload': 0
}

# in this loop:
# clients
# clientgroups total/idle/busy
for slot in slots:
#	print slot
	slotState=3
	slotStateText='UNKNOWN'
	# these are just guesses
	if slot['Activity'] in ['Busy','Idle','Benchmarking']:
		slotState=0
		slotStateText='OK'
	if slot['Activity'] in ['None','Retiring','Vacating','Suspended']:
		slotState=1
		slotStateText='WARNING'
	if slot['Activity'] in ['Killing']:
		slotState=2
		slotStateText='CRITICAL'
		
	print str(slotState) + ' Condor_slot_' + slot['Name'] + ' state=' + str(slot['Activity']) + ' ' + slotStateText + ' - slot ' + slot['Name'] + ' in clientgroup ' + slot['CLIENTGROUP'] + ' is in state ' + slot['Activity']
	slotCounts[slot['CLIENTGROUP']] += 1

schedddaemon = collector.locateAll(htcondor.DaemonTypes.Schedd)[0]

schedd = htcondor.Schedd(schedddaemon)
jobs = schedd.query()

runningJobCount=0

# in this loop:
# jobs queued/queued time (is this idle?)
# jobs in progress/in progress time
# jobs held
for job in jobs:
    if job['JobStatus'] != 4:
	try:
		jobname=job['JobBatchName']
	except:
		jobname=job['GlobalJobId']
	try:
		acctgroup=job['AcctGroup']
	except:
		acctgroup='undefined'
#	print jobname + ' : ' + acctgroup + ' ' + str(job['JobStatus'])
    if job['JobStatus'] == 2:
	runningJobCount += 1

#print str(runningJobCount) + ' running jobs'
#print slotCounts
