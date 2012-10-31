import subprocess
from time import sleep
import re

output = subprocess.check_output(["avira-deploy",  "status"])

# first destroy all ramnodes
disknode_ids = [] 
for x in output.split("\n"):
    row = re.split("\s+", x)
    if len(row) > 1:
        if "ramnode" in row[1]:
            print subprocess.check_output(["avira-deploy",  "destroy", row[2]])
        elif "disknode" in row[1]:
	    disknode_ids.append(row[2])
for disknode_id in disknode_ids:
    print subprocess.check_output(["avira-deploy",  "destroy", disknode_id])
