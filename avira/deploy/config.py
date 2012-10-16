#PEP8 --ignore=E501
import ConfigParser
import os


def init(provider=None, configfile=""):
    if configfile:
        config = ConfigParser.RawConfigParser()
        config.add_section('main')
        config.set('main', 'provider', provider)
        config.set('main', 'puppetmaster', '')
        config.set('main', 'puppetmaster_verified', '0')
        config.set('main', 'cleanup_timeout', 20)
        config.add_section('puppetbot')
        config.set('puppetbot', 'puppet_binary', '/usr/bin/puppet')
        config.set('puppetbot', 'puppet_cert_directory', '/var/lib/puppet/ssl/ca/requests')
        config.set('puppetbot', 'cert_req', '/var/lib/puppet/cert_req.txt')
        config.add_section('fabric')
        config.set('fabric', 'puppetmaster_ssh_port', '')

        if provider == "cloudstack":
            config.add_section('cloudstack')
            config.set('cloudstack', 'apiurl', 'http://mgmt1-dtc1.avira-cloud.net:8080/client/api')
            config.set('cloudstack', 'apikey', '')
            config.set('cloudstack', 'secretkey', '')
            config.set('cloudstack', 'domainid', '29')
            config.set('cloudstack', 'zoneid', '6')
            config.set('cloudstack', 'templateid', '519')
            config.set('cloudstack', 'serviceid', '17')
            config.set('cloudstack', 'cloudinit_puppet', 'http://joe.avira-cloud.net/autodeploy/vdt-puppet-agent.cloudinit')
            config.set('cloudstack', 'cloudinit_base', 'http://joe.avira-cloud.net/autodeploy/vdt-base.cloudinit')
        with open(configfile, 'wb') as f:
            config.write(f)
        f.close()

configfile = "%s/.aviradeployment.cfg" % os.path.expanduser("~")
if os.path.exists(configfile):
    config = ConfigParser.RawConfigParser()
    config.read(configfile)
    PROVIDER = config.get('main', 'provider')
    if PROVIDER == 'cloudstack':
        APIURL = config.get('cloudstack', 'apiurl')
        APIKEY = config.get('cloudstack', 'apikey')
        SECRETKEY = config.get('cloudstack', 'secretkey')
        DOMAINID = config.get('cloudstack', 'domainid')
        ZONEID = config.get('cloudstack', 'zoneid')
        TEMPLATEID = config.get('cloudstack', 'templateid')
        SERVICEID = config.get('cloudstack', 'serviceid')
        CLOUDINIT_PUPPET = config.get('cloudstack', 'cloudinit_puppet')
        CLOUDINIT_BASE = config.get('cloudstack', 'cloudinit_base')

    PUPPETMASTER = config.get('main', 'puppetmaster')
    PUPPETMASTER_VERIFIED = config.get('main', 'puppetmaster_verified')
    CLEANUP_TIMEOUT = int(config.get('main', 'cleanup_timeout'))

    PUPPET_BINARY = config.get('puppetbot', 'puppet_binary')
    PUPPET_CERT_DIRECTORY = config.get('puppetbot', 'puppet_cert_directory')
    CERT_REQ = config.get('puppetbot', 'cert_req')

    PUPPETMASTER_SSH_PORT = config.get('fabric', 'puppetmaster_ssh_port')
