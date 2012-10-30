import subprocess
from time import sleep
import re

output = subprocess.check_output(["avira-deploy",  "status"])

for x in output.split("\n"):
    row = re.split("\s+", x)
    if len(row) > 1:
        if "ramnode" in row[1] or "disknode" in row[1]:
           print subprocess.check_output(["avira-deploy",  "destroy", row[2]])
           sleep(1)
