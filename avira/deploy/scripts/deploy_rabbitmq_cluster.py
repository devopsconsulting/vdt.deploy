import subprocess
from time import sleep

print subprocess.check_output(["avira-deploy",  "deploy",  "rabbitmqdisknode",  "role=rabbitmqdisknode", "environment=oe_dev"])
sleep(2)
for i in range(1,25):
    print subprocess.check_output(["avira-deploy",  "deploy",  "rabbitmqramnode%s" % i,  "role=rabbitmqramnode", "environment=oe_dev"])
    sleep(1)
