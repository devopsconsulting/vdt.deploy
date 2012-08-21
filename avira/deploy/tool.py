#! /usr/bin/python
import cmd
import subprocess
import sys

from cloudstack.client import Client

from avira.deploy import api, pretty
from avira.deploy.clean import run_machine_cleanup, \
    remove_machine_port_forwards, node_clean, clean_foreman
from avira.deploy.config import APIURL, APIKEY, SECRETKEY, DOMAINID, ZONEID, \
    TEMPLATEID, SERVICEID, CLOUDINIT_PUPPET, CLOUDINIT_BASE, PUPPETMASTER, \
    PUPPETMASTER_VERIFIED
from avira.deploy.userdata import UserData
from avira.deploy.utils import find_by_key, add_pending_certificate, \
    find_machine, wrap, sort_by_key, is_puppetmaster, check_call_with_timeout


class CloudstackDeployment(api.CmdApi):
    """Cloudstack Deployment CMD Tool"""
    prompt = "deploy> "

    def __init__(self):
        self.debug = False
        self.client = Client(APIURL, APIKEY, SECRETKEY)
        cmd.Cmd.__init__(self)

    def do_status(self, all=False):
        """
        Shows running instances, specify 'all' to show all instances

        Usage::

            deploy> status [all]
        """
        machines = self.client.listVirtualMachines({
            'domainid': DOMAINID
        })
        machines = sort_by_key(machines, 'displayname')
        if not all:
            ACTIVE = ['Running', 'Stopping', 'Starting']
            machines = [x for x in machines if x['state'] in ACTIVE]

        pretty.machine_print(machines)

    def do_deploy(self, displayname, base=False, networkids="", **userdata):
        """
        Create a vm with a specific name and add some userdata.

        Optionally specify extra network ids.

        Usage::

            deploy> deploy <displayname> <userdata>
                    optional: <networkids> <base>

        To specify the puppet role in the userdata, which will install and
        configure the machine according to the specified role use::

            deploy> deploy loadbalancer1 role=lvs

        To specify additional user data, specify additional keywords::

            deploy> deploy loadbalancer1 role=lvs environment=test etc=more

        This will install the machine as a Linux virtual server.

        You can also specify additional networks using the following::

            deploy> deploy loadbalancer1 role=lvs networkids=312,313

        if you don't want pierrot-agent (puppet agent) automatically installed,
        you can specify 'base' as a optional parameter. This is needed for the
        puppetmaster which needs manual installation::

            deploy> deploy puppetmaster role=puppetmaster base

        """
        if not userdata:
            print "Specify the machine userdata, (at least it's role)"
            return

        vms = self.client.listVirtualMachines({
            'domainid': DOMAINID
        })

        KILLED = ['Destroyed', 'Expunging']
        existing_displaynames = \
            [x['displayname'] for x in vms if x['state'] not in KILLED]

        if displayname not in existing_displaynames:
            cloudinit_url = CLOUDINIT_BASE if base else CLOUDINIT_PUPPET

            args = {
                'serviceofferingid': SERVICEID,
                'templateid': TEMPLATEID,
                'zoneid': ZONEID,
                'domainid': DOMAINID,
                'displayname': displayname,
                'userdata': UserData(cloudinit_url,
                                     PUPPETMASTER,
                                     **userdata).base64(),
                'networkids': networkids,
            }

            response = self.client.deployVirtualMachine(args)

            # we add the machine id to the cert req file, so the puppet daemon
            # can sign the certificate
            if not base:
                add_pending_certificate(response['id'])

            print "%s started, machine id %s" % (displayname, response['id'])

        else:
            print "A machine with the name %s already exists" % displayname

    def do_destroy(self, machine_id):
        """
        Destroy a machine.

        Usage::

            deploy> destroy <machine_id>
        """

        machines = self.client.listVirtualMachines({
            'domainid': DOMAINID
        })

        machine = find_machine(machine_id, machines)

        if machine is None:
            print "No machine found with the id %s" % machine_id
        else:
            if is_puppetmaster(machine.id):
                print "You are not allowed to destroy the puppetmaster"
                return
            print "running cleanup job on %s." % machine.name
            run_machine_cleanup(machine)

            print "Destroying machine with id %s" % machine.id
            self.client.destroyVirtualMachine({
                'id': machine.id
            })

            # first we are also going to remove the portforwards
            remove_machine_port_forwards(machine, self.client)

            # now we cleanup the puppet database and certificates
            print "running puppet node clean"
            node_clean(machine)

            # now clean all offline nodes from foreman
            clean_foreman()

    def do_clean(self, _=None):
        """
        Clean expunged hosts from foreman
        """
        clean_foreman()

    def do_start(self, machine_id):
        """
        Start a stopped machine.

        Usage::

            deploy> start <machine_id>
        """

        machines = self.client.listVirtualMachines({
            'domainid': DOMAINID
        })
        machine = find_machine(machine_id, machines)

        if machine is not None:
            print "starting machine with id %s" % machine.id
            self.client.startVirtualMachine({'id': machine.id})
        else:
            print "machine with id %s is not found" % machine_id

    def do_stop(self, machine_id):
        """
        Stop a running machine.

        Usage::

            deploy> stop <machine_id>
        """

        machines = self.client.listVirtualMachines({
            'domainid': DOMAINID
        })
        machine = find_machine(machine_id, machines)

        if machine is not None:
            print "stopping machine with id %s" % machine.id
            self.client.stopVirtualMachine({'id': machine.id})
        else:
            print "machine with id %s is not found" % machine_id

    def do_reboot(self, machine_id):
        """
        Reboot a running machine.

        Usage::

            deploy> reboot <machine_id>
        """

        machines = self.client.listVirtualMachines({
            'domainid': DOMAINID
        })
        machine = find_machine(machine_id, machines)

        if machine is not None:
            print "rebooting machine with id %s" % machine.id
            self.client.rebootVirtualMachine({'id': machine.id})
        else:
            print "machine with id %s is not found" % machine_id

    def do_list(self, resource_type):
        """
        List information about current cloudstack configuration.

        Usage::

            deploy> list <templates|serviceofferings|
                          diskofferings|ip|networks|portforwardings>
        """

        if resource_type == "templates":
            zone_map = {x['id']: x['name'] for x in self.client.listZones({})}
            templates = self.client.listTemplates({
                "templatefilter": "executable"
            })
            templates = sort_by_key(templates, 'name')
            pretty.templates_print(templates, zone_map)

        elif resource_type == "serviceofferings":
            serviceofferings = self.client.listServiceOfferings()
            pretty.serviceofferings_print(serviceofferings)

        elif resource_type == "diskofferings":
            diskofferings = self.client.listDiskOfferings()
            pretty.diskofferings_print(diskofferings)

        elif resource_type == "ip":
            ipaddresses = self.client.listPublicIpAddresses()
            pretty.public_ipaddresses_print(ipaddresses)

        elif resource_type == "networks":
            networks = self.client.listNetworks({
                'zoneid': ZONEID
            })
            networks = sort_by_key(networks, 'id')
            pretty.networks_print(networks)

        elif resource_type == "portforwardings":
            portforwardings = self.client.listPortForwardingRules({
                'domain': DOMAINID
            })
            portforwardings = sort_by_key(portforwardings, 'privateport')
            portforwardings.reverse()
            pretty.portforwardings_print(portforwardings)

        else:
            print "Not implemented"

    def do_request(self, request_type):
        """
        Request a public ip address on the virtual router

        Usage::

            deploy> request ip
        """
        if request_type == "ip":
            response = self.client.associateIpAddress({
                'zoneid': ZONEID
            })
            print "created ip address with id %(id)s" % response

        else:
            print "Not implemented"

    def do_release(self, request_type, release_id):
        """
        Release a public ip address with a specific id.

        Usage::

            deploy> release ip <release_id>
        """
        if request_type == "ip":
            response = self.client.disassociateIpAddress({
                'id': release_id
            })
            print "releasing ip address, job id: %(jobid)s" % response
        else:
            print "Not implemented"

    def do_portfw(self, machine_id, ip_id, public_port, private_port):
        """
        Create a portforward for a specific machine and ip

        Usage::

            deploy> portfw <machine id> <ip id> <public port> <private port>

        You can get the machine id by using the following command::

            deploy> status

        You can get the listed ip's by using the following command::

            deploy> list ip
        """

        self.client.createPortForwardingRule({
            'ipaddressid': ip_id,
            'privateport': private_port,
            'publicport': public_port,
            'protocol': 'TCP',
            'virtualmachineid': machine_id
        })
        print "added portforward for machine %s (%s -> %s)" % (
            machine_id, public_port, private_port)

    def do_ssh(self, machine_id):
        """
        Make a machine accessible through ssh.

        Usage::

            deploy> ssh <machine_id>

        This adds a port forward under the machine id to port 22 on the machine
        eg:

        machine id is 5034, after running::

            deploy> ssh 5034

        I can now access the machine though ssh on all my registered ip
        addresses as follows::

            ssh ipaddress -p 5034
        """
        machines = self.client.listVirtualMachines({
            'domainid': DOMAINID
        })
        machine = find_machine(machine_id, machines)
        if machine is None:
            print "machine with id %s is not found" % machine_id
            return

        portforwards = wrap(self.client.listPortForwardingRules())

        def select_ssh_pfwds(pf):
            return pf.virtualmachineid == machine.id and pf.privateport == '22'
        existing_ssh_pfwds = filter(select_ssh_pfwds, portforwards)

        # add the port forward to each public ip, if it doesn't exist yet.
        ips = wrap(self.client.listPublicIpAddresses()['publicipaddress'])
        for ip in ips:
            current_fw = find_by_key(existing_ssh_pfwds, ipaddressid=ip.id)
            if current_fw is not None:
                print "machine %s already has a ssh portforward with ip %s" % (
                    machine_id, ip.ipaddress)
                continue
            else:
                self.client.createPortForwardingRule({
                    'ipaddressid': ip.id,
                    'privateport': "22",
                    'publicport': machine.id,
                    'protocol': 'TCP',
                    'virtualmachineid': machine.id
                })
                print "machine %s is now reachable (via %s:%s)" % (
                    machine_id, ip.ipaddress, machine_id)

    def do_kick(self, machine_id=None, role=None):
        """
        Trigger a puppet run on a server.

        This command only works when used on the puppetmaster.
        The command will either kick a single server or all server with a
        certian role.

        Usage::

            deploy> kick <machine_id>

        or::

            deploy> kick role=<role>

        """
        KICK_CMD = ['mco', "puppetd", "runonce", "-F"]
        if role is not None:
            KICK_CMD.append("role=%s" % role)
        else:
            machines = self.client.listVirtualMachines({
                'domainid': DOMAINID
            })
            machine = find_machine(machine_id, machines)
            KICK_CMD.append('hostname=%(name)s' % machine)

        try:
            print subprocess.check_output(KICK_CMD, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print e.output

    def do_quit(self, _=None):
        """
        Quit the deployment tool.

        Usage::

            deploy> quit
        """
        sys.exit(0)

    def do_mco(self, *args, **kwargs):
        """
        Run mcollective

        Usage::

            deploy> mco find all
            deploy> mco puppetd status -F role=puppetmaster
        """
        command = ['mco'] + list(args) + ['%s=%s' % (key, value) for (key, value) in kwargs.iteritems()]
        print command
        check_call_with_timeout(command, 5)


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
