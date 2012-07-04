from deploy import CloudstackDeployment
from functools import wraps as wraps
import subprocess
from config import PUPPETMASTER_SSH_PORT

from fabric.api import *

PUPPETMASTER_IPADDRESS = subprocess.check_output(['python', 'deploy.py', 'list', 'ip']).split()[1]
env.hosts = ["%(PUPPETMASTER_IPADDRESS)s:%(PUPPETMASTER_SSH_PORT)s" % locals()]
env.user = 'root'

__all__ = ('status', 'deploy', 'destroy', 'start', 'stop', 'reboot', 'list',
           'request', 'release', 'kick', 'ssh')

@wraps(CloudstackDeployment.do_status)
def status(all=''):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py status %(all)s' % locals())

@wraps(CloudstackDeployment.do_deploy)
def deploy(name, cloudinit_config='', **kwargs):
    kwargs_string = " ".join(["%s=%s" % (key.replace('puppet', ''), value) for key, value in kwargs.items()])
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py deploy %(name)s %(kwargs_string)s %(cloudinit_config)s' % locals())

@wraps(CloudstackDeployment.do_destroy)
def destroy(machine_id):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py destroy %(machine_id)s' % locals())

@wraps(CloudstackDeployment.do_start)
def start(machine_id):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py start %(machine_id)s' % locals())

@wraps(CloudstackDeployment.do_stop)
def stop(machine_id):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py stop %(machine_id)s' % locals())

@wraps(CloudstackDeployment.do_reboot)
def reboot(machine_id):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py reboot %(machine_id)s' % locals())

@wraps(CloudstackDeployment.do_list)
def list(type):
    allowed_types = ['templates', 'serviceofferings', 'diskofferings', 'ip']
    if type in allowed_types:
        with cd('/usr/local/src/avira.deploy'):
            run('python deploy.py list %(type)s' % locals())
    else:
        print "type should be one of %(allowed_types)s" % locals()

@wraps(CloudstackDeployment.do_request)
def request(ip):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py request %(ip)s' % locals())

@wraps(CloudstackDeployment.do_release)
def release(ip):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py release %(ip)s' % locals())

@wraps(CloudstackDeployment.do_kick)
def kick(machine_id):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py kick %(machine_id)s' % locals())

@wraps(CloudstackDeployment.do_kick)
def ssh(machine_id):
    with cd('/usr/local/src/avira.deploy'):
        run('python deploy.py ssh %(machine_id)s' % locals())
