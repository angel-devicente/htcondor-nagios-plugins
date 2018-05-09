import htcondor

schedd = htcondor.Schedd()
jobs = schedd.query()

#for job in jobs:
#    print job

collector = htcondor.Collector()
slots = collector.query(htcondor.AdTypes.Startd, "true")

for slot in slots:
        print slot['CLIENTGROUP']
