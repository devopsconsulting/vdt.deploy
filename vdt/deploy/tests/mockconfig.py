class MockConfig(object):
    PROVIDER = "cloudstack"
    PUPPETMASTER = "localhost"
    PUPPETMASTER_VERIFIED = "1"
    CLEANUP_TIMEOUT = 20

    PUPPET_BINARY = "/usr/bin/puppet"
    PUPPET_CERT_DIRECTORY = "/tmp"
    CERT_REQ = "/tmp/cert_req.txt"

    APIURL = "apiurl"
    APIKEY = "apikey"
    SECRETKEY = "secret"
    DOMAINID = "1"
    SERVICEID = "1"
    TEMPLATEID = "1"
    ZONEID = "1"
    DOMAINID = "1"
    CLOUDINIT_PUPPET = "http://localhost/autodeploy/vdt-puppet-agent.cloudinit"
    CLOUDINIT_BASE = "http://localhost/autodeploy/vdt-puppet-base.cloudinit"

    @classmethod
    def update(self, values):
        for key, value in values:
            setattr(key.upper(), value)