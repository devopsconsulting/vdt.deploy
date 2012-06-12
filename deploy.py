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
        "Shows running instances, specify 'all' to show all instances"
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
        "Usage : deploy <name> <userdata> optional: <cloudinit config>"
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
        "Usage : destroy <machine id>"
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
        "Usage : deploy <machine id>"
        if not line:
            print "Specify the machine id"
            return
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machine_ids = [str(x['id']) for x in response]
        if not line in machine_ids:
            print "Machine with id %s is not found" % line
            return
        response = self.client.startVirtualMachine({'id': line})
        print "starting machine with id %s" % line

    def do_list(self, line):
        "Usage : list <value>"
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
        "Request <type>, for example 'ip'"
        if line == "ip":
            args = {'zoneid': ZONEID}
            response = self.client.associateIpAddress(args)
            print "created ip address with id %s" % response['id']
            return
        print "Not implemented"

    def do_release(self, line):
        "Release <type> <id>, for example 'ip'"
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
        "Quit the deployment tool"
        sys.exit(0)

    def do_kick(self, line):
        "Kick a server"
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
        "Usage: ssh <ip id> <machine id>"
        cmdargs = line.split()
        ip_id = cmdargs[0]
        machine_id = cmdargs[1]
        machines = self.client.listVirtualMachines({'domainid': DOMAINID})
        machines = [x['id'] for x in machines]
        ips = self.client.listPublicIpAddresses()
        ips = [x['id'] for x in ips['publicipaddress']]
        if not int(ip_id) in ips:
            print "no ip found with id %s" % ip_id
            return
        if not int(machine_id) in machines:
            print "no machine found with id %s" % machine_id
            return
        self.client.createPortForwardingRule({
            'ipaddressid': ip_id,
            'privateport': "22",
            'publicport': machine_id,
            'protocol': 'TCP',
            'virtualmachineid': machine_id})
        print "machine %s is now reachable (via port %s)" % (machine_id,
                                                             machine_id)
        return


if __name__ == '__main__':
    if len(sys.argv) > 1:
        line = " ".join(sys.argv[1:])
        CloudstackDeployment().onecmd(line)
    else:
        CloudstackDeployment().cmdloop()
