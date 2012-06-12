#PEP8 --ignore=E501
import os
import ConfigParser

configfile = "%s/.aviradeployment.cfg" % os.path.expanduser("~")
if not os.path.isfile(configfile):
    config = ConfigParser.RawConfigParser()
    config.add_section('deployment')
    config.set('deployment', 'apiurl', 'http://mgmt1-dtc1.avira-cloud.net:8080/client/api')
    config.set('deployment', 'apikey', '')
    config.set('deployment', 'secretkey', '')
    config.set('deployment', 'domainid', '29')
    config.set('deployment', 'zoneid', '6')
    config.set('deployment', 'templateid', '392')
    config.set('deployment', 'serviceid', '17')
    config.set('deployment', 'cloudinit_puppet', 'http://joe.avira-cloud.net/autodeploy/vdt-puppet-agent.cloudinit')
    config.set('deployment', 'cloudinit_base', 'http://joe.avira-cloud.net/autodeploy/vdt-base.cloudinit')
    config.add_section('signbot')
    config.set('signbot', 'puppet_cert_directory', '/var/lib/puppet/')
    with open(configfile, 'wb') as f:
        config.write(f)
        f.close()

config = ConfigParser.RawConfigParser()
config.read(configfile)
APIURL = config.get('deployment', 'apiurl')
APIKEY = config.get('deployment', 'apikey')
SECRETKEY = config.get('deployment', 'secretkey')
DOMAINID = config.get('deployment', 'domainid')
ZONEID = config.get('deployment', 'zoneid')
TEMPLATEID = config.get('deployment', 'templateid')
SERVICEID = config.get('deployment', 'serviceid')
CLOUDINIT_PUPPET = config.get('deployment', 'cloudinit_puppet')
CLOUDINIT_BASE = config.get('deployment', 'cloudinit_base')
PUPPET_CERT_DIRECTORY = config.get('signbot', 'puppet_cert_directory')
