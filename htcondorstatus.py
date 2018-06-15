#!/usr/bin/python

import sys
import configparser
import htcondor

# magic numbers:
# https://htcondor-wiki.cs.wisc.edu/index.cgi/wiki?p=MagicNumbers

configfile=sys.argv[1]
conf=configparser.ConfigParser()
conf.read(configfile)
#print conf.sections()

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

# generate these on the fly in the slot or job loop
jobCounts = {
	'njs': 0,
	'bigmemlong': 0,
	'bigmem': 0,
	'kb_upload': 0
}
slotCounts = {}

# in this loop:
# clients (done)
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
	# need to check for this key, and create if not exists
	if slot['CLIENTGROUP'] not in slotCounts:
		slotCounts[slot['CLIENTGROUP']] = {}
		slotCounts[slot['CLIENTGROUP']]['Total'] = 0
	slotCounts[slot['CLIENTGROUP']]['Total'] += 1
	if slot['Activity'] not in slotCounts[slot['CLIENTGROUP']]:
		slotCounts[slot['CLIENTGROUP']][slot['Activity']] = 0
	slotCounts[slot['CLIENTGROUP']][slot['Activity']] += 1

# this doesn't pick up clientgroups in condor but not in config file
for clientgroup in conf.sections():
	if clientgroup in ['DEFAULT','global']:
		continue
	try:
		clientgroupState=3
		clientgroupStateText='UNKNOWN'

		if slotCounts[clientgroup]['Total'] >= conf.getint(clientgroup,'minTotal.warn'):
			clientgroupState=0
			clientgroupStateText='OK'
		if slotCounts[clientgroup]['Total'] < conf.getint(clientgroup,'minTotal.warn'):
			clientgroupState=1
			clientgroupStateText='WARNING'
		if slotCounts[clientgroup]['Total'] < conf.getint(clientgroup,'minTotal.crit'):
			clientgroupState=2
			clientgroupStateText='CRITICAL'
		if slotCounts[clientgroup]['Idle'] >= conf.getint(clientgroup,'minIdle.warn'):
			clientgroupState=0
			clientgroupStateText='OK'
		if slotCounts[clientgroup]['Idle'] < conf.getint(clientgroup,'minIdle.warn'):
			clientgroupState=1
			clientgroupStateText='WARNING'
		if slotCounts[clientgroup]['Idle'] < conf.getint(clientgroup,'minIdle.crit'):
			clientgroupState=2
			clientgroupStateText='CRITICAL'

#		print str(clientgroupState) + ' Condor_clientgroup_' + clientgroup + ' - ' + clientgroupStateText + ' - clientgroup ' + clientgroup + ' has ' + str(slotCounts[clientgroup]['Total']) + ' total workers and ' + str(slotCounts[clientgroup]['Idle']) + ' idle workers'
		print "%d Condor_clientgroup_%s %s=%d;%d;%d;0 %s - clientgroup %s has %d total workers and %d idle workers" % (clientgroupState,clientgroup,clientgroup,slotCounts[clientgroup]['Idle'],conf.getint(clientgroup,'minIdle.warn'),conf.getint(clientgroup,'minIdle.crit'),clientgroupStateText,clientgroup,slotCounts[clientgroup]['Total'],slotCounts[clientgroup]['Idle'])

	except:
		print str(3) + ' Condor_clientgroup_' + clientgroup + ' - UNKNOWN - clientgroup ' + clientgroup + ' has no workers in any state'

schedddaemon = collector.locateAll(htcondor.DaemonTypes.Schedd)[0]

schedd = htcondor.Schedd(schedddaemon)
jobs = schedd.query()

# need to make these clientgroup-specific?
runningJobCount=0
idleJobCount=0

# in this loop:
# jobs queued/queued time (is this idle?) (still to do)
# jobs in progress/in progress time (still to do)
# jobs held (still to do)
for job in jobs:
    numIdleState=3
    numIdleStateText='UNKNOWN'
    idleTimeState=3
    idleTimeStateText='UNKNOWN'
    numRunningState=3
    numRunningStateText='UNKNOWN'
    runningTimeState=3
    runningTimeStateText='UNKNOWN'

    jobname='[undefined]'
    acctgroup='[undefined]'
    try:
	jobname=job['JobBatchName']
    except:
	jobname=job['GlobalJobId']
    try:
	acctgroup=job['AcctGroup']
    except:
	acctgroup='undefined'
#	print jobname + ' : ' + acctgroup + ' ' + str(job['JobStatus'])
# 2 is running; alert on long run times
    if job['JobStatus'] == 2:
	if job['ServerTime'] - job['JobStartDate'] > conf.getint('global','runtime.warn'):
		runningTimeState=1
	if job['ServerTime'] - job['JobStartDate'] > conf.getint('global','runtime.crit'):
		runningTimeState=2
	runningJobCount += 1
# 1 is idle; alert on long queue times
    if job['JobStatus'] == 1:
	if job['ServerTime'] - job['QDate'] > conf.getint('global','idletime.warn'):
		runningTimeState=1
	if job['ServerTime'] - job['QDate'] > conf.getint('global','idletime.crit'):
		runningTimeState=2
	idleJobCount += 1
#    print jobname
#    print job['JobStartDate']
#    print job['QDate']
#    print job['ServerTime']
	
#print str(runningJobCount) + ' running jobs'
#print slotCounts
