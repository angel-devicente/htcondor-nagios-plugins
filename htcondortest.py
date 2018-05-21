import htcondor

collector = htcondor.Collector()
slots = collector.query(htcondor.AdTypes.Startd, "true")

counts = {
	'njs': 0,
	'bigmemlong': 0,
	'bigmem': 0,
	'kb_upload': 0
}

# in this loop:
# clients
# clientgroups total/idle/busy
for slot in slots:
        print slot['Name'] + ' : ' + slot['CLIENTGROUP'] + ' ' + slot['Activity']
	counts[slot['CLIENTGROUP']] += 1

# super hacky
schedddaemon = collector.locateAll(htcondor.DaemonTypes.Schedd)[0]

schedd = htcondor.Schedd(schedddaemon)
jobs = schedd.query()

runningJobCount=0

# in this loop:
# jobs queued/queued time (is this idle?)
# jobs in progress/in progress time
# jobs held
for job in jobs:
# http://pages.cs.wisc.edu/~adesmet/status.html
#Job Status
#JobStatus in job ClassAds
#
#0	Unexpanded	U
#1	Idle	I
#2	Running	R
#3	Removed	X
#4	Completed	C
#5	Held	H
#6	Submission_err	E
    if job['JobStatus'] != 4:
        print job['JobBatchName'] + ' : ' + job['AcctGroup'] + ' ' + str(job['JobStatus'])
    if job['JobStatus'] == 2:
	runningJobCount += 1

print str(runningJobCount) + ' running jobs'
print counts
