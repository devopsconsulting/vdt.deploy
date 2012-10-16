#PEP8 --ignore=E501
import ConfigParser
import os

configfile = "%s/.aviradeployment.cfg" % os.path.expanduser("~")

main_template = """# configuration setting for avira-deploy
[main]
provider = cloudstack
puppetmaster =
puppetmaster_verified =
cleanup_timeout = 20

[puppetbot]
puppet_binary = /usr/bin/puppet
puppet_cert_directory = /var/lib/puppet/ssl/ca/requests
cert_req = /var/lib/puppet/cert_req.txt

[fabric]
puppetmaster_ssh_port = 22"""


class Config(object):

    def __init__(self):
        if os.path.exists(configfile):
            config = ConfigParser.RawConfigParser()
            config.read(configfile)
            for section in config.sections():
                for item in config.items(section):
                    setattr(self, item[0].upper(), item[1])
