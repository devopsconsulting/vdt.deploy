import itertools
import subprocess

from avira.deploy.config import PUPPET_BINARY
from avira.deploy.utils import wrap


def run_machine_cleanup(machine):
    try:
        print subprocess.check_output([
            'mco', 'rpc', '-v', 'cleanup', 'cleanup', '-F', 'hostname=%s' %
            machine.name
        ])
    except subprocess.CalledProcessError as e:
        print "An error occurred while running cleanup: %s" % \
            e.output


def remove_machine_port_forwards(machine, client):
    response = wrap(client.listPortForwardingRules())
    for portforward in response:
        if portforward.virtualmachineid == machine.id:
            print "Removing portforward %s:%s -> %s" % (
                portforward.ipaddress,
                portforward.publicport,
                portforward.privateport
            )

            args = {'id': portforward.id}
            client.deletePortForwardingRule(args)


def clean_fqdn(fqdn, *extra_flags, **extra_kw_flags):
    command = [PUPPET_BINARY, "node", "clean"]

    flags = ["--%s" % flag for flag in extra_flags]
    command += flags

    kw_flags = [("--%s" % keys, val) for key, val in extra_kw_flags.items()]
    command += itertools.chain.from_iterable(kw_flags)

    command.append(fqdn)
    return subprocess.check_output(command)


def node_clean(machine):
    puppetcerts = \
        subprocess.check_output([PUPPET_BINARY, 'cert', '--list', '--all'])
    puppetcerts = puppetcerts.split("\n")
    puppetcert_names = \
        [x.split()[1] for x in puppetcerts if x and machine.name.lower() in x]
    for cert_name in puppetcert_names:
        if machine.name.lower() in cert_name:
            print clean_fqdn(cert_name, 'unexport')
            print clean_fqdn(cert_name)
