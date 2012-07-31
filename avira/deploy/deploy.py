#! /usr/bin/python
import sys
import os
import cmd
import subprocess
from CloudStack.Client import Client
from config import APIURL, APIKEY, SECRETKEY, DOMAINID, ZONEID, TEMPLATEID, \
                   SERVICEID, CLOUDINIT_PUPPET, CLOUDINIT_BASE, \
                   CERT_REQ, PUPPET_BINARY, PUPPETMASTER, PUPPETMASTER_VERIFIED
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

    def _add_cert_machine(self, machine_id):
        machine_id = str(machine_id)
        ids = []
        if os.path.exists(CERT_REQ):
            f = open(CERT_REQ, "r")
            ids = [x for x in f.read().split('\n') if not x == '']
            f.close()
        if not machine_id in ids:
            ids.append(machine_id)
        data = "\n".join(ids)
        f = open(CERT_REQ, "w")
        f.write(data)
        f.close()

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

        Optionally specify extra network ids.

        Usage::

            deploy> deploy <name> <userdata>
                    optional: <network ids> <base>

        To specify the puppet role in the userdata, which will install and
        configure the machine according to the specified role use::

            deploy> deploy loadbalancer1 role=lvs

        This will install the machine as a Linux virtual server.

        You can also specify additional networks using the following::

            deploy> deploy loadbalancer1 role=lvs networks=312,313

        if you don't want pierrot-agent (puppet agent) automatically installed,
        you can specify 'base' as a optional parameter. This is needed for the
        puppetmaster which needs manual installation::

            deploy> deploy puppetmaster role=puppetmaster base

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
        initial_machine = False
        CLOUDINIT_URL = CLOUDINIT_PUPPET
        args = {'serviceofferingid': SERVICEID,
                'templateid': TEMPLATEID,
                'zoneid': ZONEID,
                'domainid': DOMAINID,
                'displayname': name,
                }
        # check for additional options
        if len(cmdargs) > 2:
            for param in cmdargs[2:]:
                # we can specify additional networks here
                if param.find("networks") == 0:
                    network_ids = param.split('=')[1].split(",")
                    args["networkids"] = network_ids
                elif param.find("base") == 0:
                    initial_machine = True
                    CLOUDINIT_URL = CLOUDINIT_BASE

        # we add the cloudinit configuration url first
        # second argument is of the format key=value,anotherkey=anothervalue
        # we put a # in front to be cloudinit compatible
        params = cmdargs[1].split(",")
        params = "\n".join(["#%s" % x for x in params])
        # now we also put the puppetmaster ip/hostname in the config
        if not initial_machine:
            puppetmaster = PUPPETMASTER
            params += "\n#puppetmaster=%s" % puppetmaster
        userdata = "#include %s\n%s" % (CLOUDINIT_URL, params)
        userdata = encodestring(userdata)
        args['userdata'] = userdata
        response = self.client.deployVirtualMachine(args)
        # we add the machine id to the cert req file, so the puppet daemon can
        # sign the certificate
        if not initial_machine:
            self._add_cert_machine(response['id'])
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
        machine = [x for x in response if str(x['id']) == line]

        if not machine:
            print "No machine found with the id %s" % line
        else:
            machine_id = str(machine[0]['id'])
            hostname = str(machine[0]['name'])
            
            # not a failsafe method of checking, but for now
            # no other solution
            fqdn = subprocess.check_output(['facter', "fqdn"])
            if machine_id in fqdn:
                print "You are not allowed to destroy the puppetmaster"    
                return
            
            print "running cleanup job on %s." % hostname
            try:
                print subprocess.check_output(['mco', 'rpc', 'cleanup', 'cleanup', '-F', 'hostname=%s' % hostname])
            except subprocess.CalledProcessError as e
                print "An error occurred while running cleanup: %s" % e.output
            
            response = self.client.destroyVirtualMachine({'id': machine_id})
            print "Destroying machine with id %s" % machine_id

            # first we are also going to remove the portforwards
            response = self.client.listPortForwardingRules()
            for portforward in response:
                if str(portforward['virtualmachineid']) == machine_id:
                    args = {'id': str(portforward['id'])}
                    self.client.deletePortForwardingRule(args)
                    ip = portforward['ipaddress']
                    print "Removing portforward %s:%s -> %s" % (ip,
                                                    portforward['publicport'],
                                                    portforward['privateport'])

            # now we cleanup the puppet database and certificates
            puppetcerts = subprocess.check_output([PUPPET_BINARY,
                                                   'cert',
                                                   '--list',
                                                   '--all'])
            puppetcerts = puppetcerts.split("\n")
            puppetcerts = [x.split(' ')[1] for x in puppetcerts if x]
            for cert in puppetcerts:
                # the machine id is in the certifiate name. NOTE! This is
                # not failsafe!
                searchstring = "-%s-" % machine_id
                if searchstring in cert:
                        res = subprocess.check_output([PUPPET_BINARY,
                                                      "node",
                                                      "clean",
                                                      "--unexport",
                                                      cert])
                        print res
                        res = subprocess.check_output([PUPPET_BINARY,
                                                      "node",
                                                      "clean",
                                                      cert])
                        print res

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
        List information about current cloudstack configuration.

        Usage::

            deploy> list <templates|serviceofferings|
                          diskofferings|ip|networks|portforwardings>
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
                print "%5s   %40s   %s" % (x['id'],
                                           x['name'],
                                           zones[x['zoneid']])
            return
        elif line == "serviceofferings":
            serviceofferings = self.client.listServiceOfferings()
            for x in serviceofferings:
                print "%5s    %s" % (x['id'],
                                     x['displaytext'],
                                 )
            return
        elif line == "diskofferings":
            diskofferings = self.client.listDiskOfferings()
            for x in diskofferings:
                print "%5s   %30s %8s" % (x['id'],
                                          x['name'],
                                          "%s GB" % x['disksize'])
            return
        elif line == "ip":
            response = self.client.listPublicIpAddresses()
            for x in response['publicipaddress']:
                print "%5s   %15s" % (x['id'],
                                      x['ipaddress'])
            return
        elif line == "networks":
            args = {'zoneid': ZONEID}
            response = self.client.listNetworks(args)
            networks = sorted(response, key=itemgetter('id'))
            for x in networks:
                print "%5s   %15s" % (x['id'],
                                      x['name'])
            return
        elif line == "portforwardings":
            args = {'domain': DOMAINID}
            response = self.client.listPortForwardingRules(args)
            portforwardings = sorted(response, key=itemgetter('privateport'))
            portforwardings.reverse()
            for x in portforwardings:
                print "%5s   %15s   %4s to %4s on machine %5s-%s" % (x['id'],
                                                x['ipaddress'],
                                                x['publicport'],
                                                x['privateport'],
                                                x['virtualmachineid'],
                                                x['virtualmachinedisplayname'])
            return
        print "Not implemented"

    def do_request(self, line):
        """
        Request a public ip address on the virtual router

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
        Release a public ip address with a specific id.

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

    def do_portfw(self, line):
        """
        Create a portforward for a specific machine and ip

        Usage::

            deploy> portfw <machine id> <ip id> <public port> <private port>

        You can get the machine id by using the following command::

            deploy> status

        You can get the listed ip's by using the following command::

            deploy> list ip
        """
        cmdargs = line.split()
        if not len(cmdargs) == 4:
            print "Please specify the correct arguments"
            return
        machine_id = cmdargs[0]
        ip_id = cmdargs[1]
        public_port = cmdargs[2]
        private_port = cmdargs[3]
        self.client.createPortForwardingRule({
            'ipaddressid': ip_id,
            'privateport': private_port,
            'publicport': public_port,
            'protocol': 'TCP',
            'virtualmachineid': machine_id})
        print "added portforward for machine %s (%s -> %s)" % (machine_id,
                                                               public_port,
                                                               private_port)

    def do_ssh(self, line):
        """
        Make a machine accessible through ssh.

        Usage::

            deploy> ssh <machine id>

        This adds a port forward under the machine id to port 22 on the machine
        eg:

        machine id is 5034, after running::

            deploy> ssh 5034

        I can now access the machine though ssh on all my registered ip
        addresses as follows::

            ssh ipaddress -p 5034
        """
        # Todo : check if portforward exists
        machine_id = line.strip()
        response = self.client.listVirtualMachines({'domainid': DOMAINID})
        machine_ids = [str(x['id']) for x in response]
        if not machine_id in machine_ids:
            print "no machine found with id %s" % machine_id
            return
        portforwards = self.client.listPortForwardingRules()
        ssh_portforwards = [x for x in portforwards \
                            if (str(x['virtualmachineid']) == machine_id and \
                                x['privateport'] == '22')]
        ips = self.client.listPublicIpAddresses()['publicipaddress']
        for ip in ips:
            current_fw = [x for x in ssh_portforwards \
                          if x['ipaddressid'] == ip['id']]
            if current_fw:
                print "machine %s already has a ssh portforward with ip %s" % \
                                                            (machine_id,
                                                             ip['ipaddress'])
                continue
            self.client.createPortForwardingRule({
                'ipaddressid': str(ip['id']),
                'privateport': "22",
                'publicport': line,
                'protocol': 'TCP',
                'virtualmachineid': line})
            print "machine %s is now reachable (via %s:%s)" % (machine_id,
                                                               ip['ipaddress'],
                                                               line)
        return

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

    def do_quit(self, line):
        """
        Quit the deployment tool.

        Usage::

            deploy> quit
        """
        sys.exit(0)


def main():
    if not PUPPETMASTER_VERIFIED == '1':
        print "\nPlease edit your configfile : \n"
        print "Set puppetmaster_verified to 1 if you are sure you run this " \
               "deployment tool on the puppetmaster."
        sys.exit(0)
    elif not PUPPETMASTER:
        print "Please specify the fqdn of the puppetmaster in the config"
        sys.exit(0)
    deploy = CloudstackDeployment()
    if len(sys.argv) > 1:
        line = " ".join(sys.argv[1:])
        deploy.onecmd(line)
    else:
        try:
            deploy.cmdloop()
        except KeyboardInterrupt:
            deploy.do_quit('now')


if __name__ == '__main__':
    main()
