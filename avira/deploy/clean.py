import itertools
import signal
import subprocess
import os.path

from avira.deploy.config import PUPPET_BINARY, CLEANUP_TIMEOUT
from avira.deploy.utils import wrap


def run_machine_cleanup(machine):
    # run cleanup but kill the process after CLEANUP_TIMEOUT has passed
    cleanup_cmd = 'mco rpc -v cleanup cleanup -F hostname=%s' % machine.name
    cleanup_ps = subprocess.Popen(cleanup_cmd.split())

    signal.signal(signal.SIGALRM, lambda _, __: cleanup_ps.terminate())
    signal.alarm(CLEANUP_TIMEOUT)

    cleanup_ps.wait()

    # remove the signal handler now.
    signal.signal(signal.SIGALRM, signal.SIG_IGN)


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


def clean_foreman():
    "clean_foreman will only remove expunged hosts"

    clean_cmd = "rake hosts:scan_out_of_sync"
    if os.path.exists("/usr/share/foreman/Rakefile"):
        ps = subprocess.Popen(clean_cmd.split(), cwd='/usr/share/foreman/')
        ps.communicate('yes')
