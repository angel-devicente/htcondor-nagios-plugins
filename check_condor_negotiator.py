#!/usr/bin/python3
# Copyright 2014 Science and Technology Facilities Council
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import htcondor
import classad
import socket

# Exit statuses recognized by Nagios
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3 

rtnMsg = ""

try:
  coll = htcondor.Collector(socket.gethostname())
  negotiators = coll.query(htcondor.AdTypes.Negotiator, "true", ["Name"])
  numNegotiators = len(negotiators)

  if numNegotiators >= 1:
    if numNegotiators == 1:
      rtnMsg = "Negotiator running on "
      exitState = OK 
    else:
      rtnMsg="More than 1 negotiator running "
      exitState = CRITICAL

    for negotiator in negotiators:
      rtnMsg += negotiator['Name'].replace(".ll.iac.es","") + " "
  else:
    rtnMsg="No negotiators running."
    exitState = CRITICAL
except Exception as e:
  rtnMsg = "Problem running check. " + str(e)
  exitState = UNKNOWN

print(rtnMsg)
exit(exitState)
