import itertools
import subprocess
import os.path
import shlex

from avira.deploy.config import PUPPET_BINARY, CLEANUP_TIMEOUT
from avira.deploy.utils import wrap, check_call_with_timeout

__all__ = ('run_machine_cleanup', 'remove_machine_port_forwards', 'clean_fqdn',
           'node_clean', 'clean_foreman')


def run_machine_cleanup(machine):
    # run cleanup but kill the process after CLEANUP_TIMEOUT has passed
    cleanup_cmd = 'mco rpc -v cleanup cleanup -F hostname=%s' % machine.name
    check_call_with_timeout(cleanup_cmd.split(),
                            timeout_seconds=CLEANUP_TIMEOUT)


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

    kw_flags = [("--%s" % key, val) for key, val in extra_kw_flags.items()]
    command += itertools.chain.from_iterable(kw_flags)

    command.append(fqdn)
    return subprocess.check_output(command)


def node_clean(machine):
    puppetcerts = \
        subprocess.check_output([PUPPET_BINARY, 'cert', '--list', '--all'])
    puppetcerts = puppetcerts.split("\n")
    puppetcert_names = \
        [shlex.split(x)[1] for x in puppetcerts if x and machine.name.lower() in x]
    for cert_name in puppetcert_names:
        if machine.name.lower() in cert_name:
            print clean_fqdn(cert_name, 'unexport')
            print clean_fqdn(cert_name)


def clean_foreman():
    "clean_foreman will only remove expunged hosts"

    clean_cmd = "rake hosts:scan_out_of_sync"
    if os.path.exists("/usr/share/foreman/Rakefile"):
        ps = subprocess.Popen(clean_cmd.split(), cwd='/usr/share/foreman/')
        ps.communicate('yes')
