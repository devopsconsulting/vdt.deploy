import subprocess
import functools

from fabric.api import *

from avira.deploy.tool import CloudstackDeployment
from avira.deploy.config import PUPPETMASTER_SSH_PORT

PUPPETMASTER_IPADDRESS = subprocess.check_output(['python', 'avira/deploy/tool.py', 'list', 'ip']).split()[1]
env.hosts = ["%(PUPPETMASTER_IPADDRESS)s:%(PUPPETMASTER_SSH_PORT)s" % locals()]
env.user = 'root'

__all__ = ('status', 'deploy', 'destroy', 'start', 'stop', 'reboot', 'list',
           'request', 'release', 'kick', 'ssh', 'portfw', 'clean', 'mco')


@functools.wraps(CloudstackDeployment.do_status)
def status(all=''):
    run('/usr/bin/avira-deploy status %(all)s' % locals())


@functools.wraps(CloudstackDeployment.do_deploy)
def deploy(name, cloudinit_config='', **kwargs):
    kwargs_string = " ".join(["%s=%s" % (key.replace('puppet', ''), value) for key, value in kwargs.items()])
    run('/usr/bin/avira-deploy deploy %(name)s %(kwargs_string)s %(cloudinit_config)s' % locals())


@functools.wraps(CloudstackDeployment.do_destroy)
def destroy(machine_id):
    run('/usr/bin/avira-deploy destroy %(machine_id)s' % locals())


@functools.wraps(CloudstackDeployment.do_clean)
def clean():
    run('/usr/bin/avira-deploy clean')


@functools.wraps(CloudstackDeployment.do_start)
def start(machine_id):
    run('/usr/bin/avira-deploy start %(machine_id)s' % locals())


@functools.wraps(CloudstackDeployment.do_stop)
def stop(machine_id):
    run('/usr/bin/avira-deploy stop %(machine_id)s' % locals())


@functools.wraps(CloudstackDeployment.do_reboot)
def reboot(machine_id):
    run('/usr/bin/avira-deploy reboot %(machine_id)s' % locals())


@functools.wraps(CloudstackDeployment.do_list)
def list(type):
    allowed_types = ['templates', 'serviceofferings', 'diskofferings', 'ip', 'portforwardings']
    if type in allowed_types:
        run('/usr/bin/avira-deploy list %(type)s' % locals())
    else:
        print "type should be one of %(allowed_types)s" % locals()


@functools.wraps(CloudstackDeployment.do_request)
def request(ip):
    run('/usr/bin/avira-deploy request %(ip)s' % locals())


@functools.wraps(CloudstackDeployment.do_release)
def release(ip):
    run('/usr/bin/avira-deploy release %(ip)s' % locals())


@functools.wraps(CloudstackDeployment.do_portfw)
def portfw(machine_id, ip_id, public_port, private_port):
    run('/usr/bin/avira-deploy portfw %(machine_id)s %(ip_id)s %(public_port)s %(private_port)s' % locals())


@functools.wraps(CloudstackDeployment.do_ssh)
def ssh(machine_id):
    run('/usr/bin/avira-deploy ssh %(machine_id)s' % locals())


@functools.wraps(CloudstackDeployment.do_kick)
def kick(machine_id=None, puppetrole=None):
    if puppetrole:
        run('/usr/bin/avira-deploy kick role=%(role)s' % locals())
    else:
        run('/usr/bin/avira-deploy kick %(machine_id)s' % locals())


@functools.wraps(CloudstackDeployment.do_mco)
def mco(*args, **kwargs):
    bar = " ".join(args)
    foo = ['%s=%s' % (key, value) for (key, value) in kwargs.iteritems()]
    run('/usr/bin/avira-deploy mco %s %s' % (bar, foo))
