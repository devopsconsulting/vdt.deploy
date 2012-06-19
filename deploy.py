#! /usr/bin/python
import sys
import cmd
import subprocess
from CloudStack.Client import Client
from config import (APIURL, APIKEY, SECRETKEY, DOMAINID, ZONEID, TEMPLATEID,
                    SERVICEID, CLOUDINIT_BASE, CLOUDINIT_PUPPET
                   )
from base64 import encodestring
from operator import itemgetter


class ServerNotFound(Exception):
    pass


class CloudstackDeployment(cmd.Cmd):
    """Cloudstack Deployment CMD Tool"""
    prompt = "deploy> "

    def __init__(self):
        self.client = Client(APIURL, APIKEY, SECRETKEY)
        cmd.Cmd.__init__(self)

    def _nic_of(self, server_name):
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        try:
            server = (s for s in response if\
                s['displayname'] == server_name).next()
            return (nic for nic in server['nic'] if nic['isdefault']).next()
        except StopIteration:
            raise ServerNotFound(
                "could not find server named %(server_name)s" % locals())

    def do_status(self, line):
        """
        Shows running instances, specify 'all' to show all instances
        
        Usage::
            
            deploy> status [all]
        """
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machines = [x for x in response if x['state'] in ['Running',
                                                          'Stopping',
                                                          'Starting']]
        if line == 'all':
            machines = [x for x in response]
        machines = sorted(machines, key=itemgetter('displayname'))
        for x in machines:
            print "%30s %15s %5s  %s" % (x['displayname'],
                                         x['name'],
                                         x['id'],
                                         x['state'])

    def do_deploy(self, line):
        """
        Create a vm with a specific name and add some userdata.
        
        Optionally specify a specific cloudinit config.
        
        Usage::
            
            deploy> deploy <name> <userdata> optional: <cloudinit config>
        
        To specify the puppet role in the userdata, which will install and
        configure the machine according to the specified role use::
        
            deploy> deploy loadbalancer1 role=lvs
        
        This will install the machine as a Linux virtual server.
        """
        if not line:
            print "Specify the machine userdata"
            return
        cmdargs = line.split()
        name = cmdargs[0]
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machines = [x['displayname'] for x in response
                    if not x['state'] in ['Destroyed', 'Expunging']]
        if name in machines:
            print "A machine with the name %s already exists" % name
            return

        # we add the cloudinit configuration url first
        # second argument is of the format key=value,anotherkey=anothervalue
        # we put a # in front to be cloudinit compatible
        params = cmdargs[1].split(",")
        params = "\n".join(["#%s" % x for x in params])
        CLOUDINIT_URL = CLOUDINIT_PUPPET
        if len(cmdargs) > 2:
            # we can specify a base installation without puppet
            if cmdargs[2] == 'base':
                CLOUDINIT_URL = CLOUDINIT_BASE
        userdata = "#include %s\n%s" % (CLOUDINIT_URL, params)
        userdata = encodestring(userdata)
        args = {'serviceofferingid': SERVICEID,
                'templateid': TEMPLATEID,
                'zoneid': ZONEID,
                'domainid': DOMAINID,
                'displayname': name,
                'userdata': userdata
                }
        response = self.client.deployVirtualMachine(args)
        print "%s started, machine id %s" % (name, response['id'])

    def do_destroy(self, line):
        """
        Destroy a machine.
        
        Usage::
            
            deploy> destroy <machine id>
        """
        if not line:
            print "Specify the machine id (status)"
            return
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machine = [x['id'] for x in response if str(x['id']) == line]
        if not machine:
            print "No machine found with the id %s" % line
        else:
            machine_id = str(machine[0])
            response = self.client.destroyVirtualMachine({'id': machine_id})
            print "destroying machine with id %s" % machine_id

    def do_start(self, line):
        """
        Start a stopped machine.
        
        Usage::
        
            deploy> start <machine id>
        """
        if not line:
            print "Specify the machine id"
            return
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machine_ids = [str(x['id']) for x in response]
        if not line in machine_ids:
            print "machine with id %s is not found" % line
            return
        response = self.client.startVirtualMachine({'id': line})
        print "starting machine with id %s" % line

    def do_stop(self, line):
        """
        Stop a running machine.
        
        Usage::
            
            deploy> stop <machine id>
        """
        if not line:
            print "Specify the machine id"
            return
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machine_ids = [str(x['id']) for x in response]
        if not line in machine_ids:
            print "machine with id %s is not found" % line
            return
        response = self.client.stopVirtualMachine({'id': line})
        print "stoping machine with id %s" % line

    def do_reboot(self, line):
        """
        Reboot a running machine.
        
        Usage::
        
            deploy> reboot <machine id>
        """
        if not line:
            print "Specify the machine id"
            return
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machine_ids = [str(x['id']) for x in response]
        if not line in machine_ids:
            print "machine with id %s is not found" % line
            return
        response = self.client.rebootVirtualMachine({'id': line})
        print "stopping machine with id %s" % line

    def do_list(self, line):
        """
        list the available templates|diskofferings|ipadresses.
        
        Usage::
            
            deploy> list <templates|diskofferings|ip>
        """
        if not line:
            print "Usage : list <value>, example : list templates"
            return
        if line == "templates":
            args = {}
            zones = self.client.listZones(args)
            zones = {x['id']: x['name'] for x in zones}
            args = {"templatefilter": "executable"}
            templates = self.client.listTemplates(args)
            templates = sorted(templates, key=itemgetter('name'))
            for x in templates:
                print "%40s %15s  %s" % (x['name'],
                                         x['id'],
                                         zones[x['zoneid']])
            return
        elif line == "diskofferings":
            diskofferings = self.client.listDiskOfferings()
            for x in diskofferings:
                print "%30s %5s %8s" % (x['name'],
                                         x['id'],
                                         "%s GB" % x['disksize'])
            return
        elif line == "ip":
            response = self.client.listPublicIpAddresses()
            for x in response['publicipaddress']:
                print "%5s   %15s" % (x['id'],
                                      x['ipaddress'])
            return
        print "Not implemented"

    def do_request(self, line):
        """
        Create an ip address.
        
        Usage::
        
            deploy> request ip
        """
        if line == "ip":
            args = {'zoneid': ZONEID}
            response = self.client.associateIpAddress(args)
            print "created ip address with id %s" % response['id']
            return
        print "Not implemented"

    def do_release(self, line):
        """
        Destroy an ip address with a specific id.
        
        Usage::
        
            deploy> release ip <id>
        """
        cmdargs = line.split()
        cmd = cmdargs[0]
        release_id = cmdargs[1]
        if cmd == "ip":
            args = {'id': release_id}
            response = self.client.disassociateIpAddress(args)
            print "release ip address requested with job id %s" % \
                                                            response["jobid"]
            return
        print "Not implemented"

    def do_quit(self, line):
        """
        Quit the deployment tool.
        
        Usage::
            
            deploy> quit
        """
        sys.exit(0)

    def do_kick(self, line):
        """
        Trigger a puppet run on a server. This command only works when used
        on the puppetmaster.
        
        Usage::
        
            deploy> kick <machine_id>
        """
        try:
            ipaddress = self._nic_of(line)['ipaddress']
            try:
                print subprocess.check_output(['puppet', "kick", ipaddress],
                    stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                print e.output
        except ServerNotFound as e:
            print e.message

    def do_ssh(self, line):
        """
        Make a machine accessible through ssh.
        
        Usage::
        
            deploy> ssh <machine id>
        
        This adds a port forward under the machine id to port 22 on the machine,
        eg:
        
        machine id is 5034, after running:
        
            deploy> ssh 5034
        
        I can now access the machine though ssh on all my registered ip
        addresses as follows:
        
            ssh ipaddress -p 5034
        """
        # Todo : check if portforward exists
        # Todo : remove portforwards on removal
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machine_ids = [str(x['id']) for x in response]
        ips = self.client.listPublicIpAddresses()['publicipaddress']
        if not line in machine_ids:
            print "no machine found with id %s" % line
            return
        for ip in ips:
            self.client.createPortForwardingRule({
                'ipaddressid': str(ip['id']),
                'privateport': "22",
                'publicport': line,
                'protocol': 'TCP',
                'virtualmachineid': line})
            print "machine %s is now reachable (via %s:%s)" % (line,
                                                               ip['ipaddress'],
                                                               line)
        return


if __name__ == '__main__':
    deploy = CloudstackDeployment()
    if len(sys.argv) > 1:
        line = " ".join(sys.argv[1:])
        deploy.onecmd(line)
    else:
        try:
            deploy.cmdloop()
        except KeyboardInterrupt:
            deploy.do_quit('now')
