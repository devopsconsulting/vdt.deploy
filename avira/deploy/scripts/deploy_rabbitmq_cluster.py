import subprocess
import re
from time import sleep

output = subprocess.check_output(["avira-deploy",  "deploy",  "rabbitmqdisknode",  "role=rabbitmqdisknode", "environment=oe_dev"])
print output
machine_id = re.split("\s+", output)[4]
output = subprocess.check_output(["avira-deploy",  "list",  "ip"])
ip_id = re.split("\s+", output)[0]
print subprocess.check_output(["avira-deploy",  "portfw",  machine_id,  ip_id, "55672", "55672"]) 
sleep(20)
for i in range(1,4):
    print subprocess.check_output(["avira-deploy",  "deploy",  "rabbitmqramnode%s" % i,  "role=rabbitmqramnode", "environment=oe_dev"])
    sleep(1)