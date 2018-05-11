import htcondor

schedd = htcondor.Schedd()
jobs = schedd.query()

runningJobCount=0

# in this loop:
# jobs queued/queued time
# jobs in progress/in progress time
#for job in jobs:
# how to detect a queued or in progres job?
#    print job

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
print counts
