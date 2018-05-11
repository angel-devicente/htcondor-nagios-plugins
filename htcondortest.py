import htcondor

schedd = htcondor.Schedd()
jobs = schedd.query()

runningJobCount=0
#for job in jobs:
#    print job

collector = htcondor.Collector()
slots = collector.query(htcondor.AdTypes.Startd, "true")

for slot in slots:
        print slot['Name'] + ' : ' + slot['CLIENTGROUP'] + ' ' + slot['Activity']
