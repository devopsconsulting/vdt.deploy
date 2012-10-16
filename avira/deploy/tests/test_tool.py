import os
import sys
import cloudstack
import mox
import testdata
import unittest
from StringIO import StringIO
import ConfigParser

os.environ["HOME"] = "/tmp"
configfile = "%s/.aviradeployment.cfg" % os.path.expanduser("~")
import avira.deploy.config


def setupConfig():
    avira.deploy.config.init("cloudstack", configfile)
    config = ConfigParser.RawConfigParser()
    config.read(configfile)
    config.set('main', 'provider', 'cloudstack')
    config.set('main', 'puppetmaster', 'localhost')
    config.set('main', 'puppetmaster_verified', '1')
    with open(configfile, 'wb') as f:
        config.write(f)
        f.close()


def removeConfig():
    configfile = "%s/.aviradeployment.cfg" % os.path.expanduser("~")
    # remove the config
    if os.path.exists(configfile):
        os.remove(configfile)

setupConfig()
import avira.deploy.tool
import avira.deploy.providers.provider_cloudstack


class ProviderCloudstackTest(unittest.TestCase):

    def setUp(self):
        self.saved_stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out
        setupConfig()
        self.mox = mox.Mox()
       # set some expected values
        avira.deploy.providers.provider_cloudstack.APIURL = "apiurl"
        avira.deploy.providers.provider_cloudstack.APIKEY = "apikey"
        avira.deploy.providers.provider_cloudstack.SECRETKEY = "secret"
        avira.deploy.providers.provider_cloudstack.DOMAINID = "1"
        avira.deploy.providers.provider_cloudstack.SERVICEID = "1"
        avira.deploy.providers.provider_cloudstack.TEMPLATEID = "1"
        avira.deploy.providers.provider_cloudstack.ZONEID = "1"
        avira.deploy.providers.provider_cloudstack.DOMAINID = "1"
        avira.deploy.providers.provider_cloudstack.PUPPETMASTER = "localhost"
        avira.deploy.providers.provider_cloudstack.PUPPETMASTER_VERIFIED = "1"
        avira.deploy.providers.provider_cloudstack.CLOUDINIT_PUPPET = \
                "http://localhost/autodeploy/vdt-puppet-agent.cloudinit"
        # and set some default userdata
        self.sample_userdata = "#include %s\n#puppetmaster=%s\n" % \
                 (avira.deploy.providers.provider_cloudstack.CLOUDINIT_PUPPET,
                  avira.deploy.providers.provider_cloudstack.PUPPETMASTER)

    def tearDown(self):
        removeConfig()
        self.mox.UnsetStubs()
        sys.stdout = self.saved_stdout
        self.out = None

    @unittest.skip("Needs refactoring of config")
    def test_main_unverified_puppetmaster(self):
        # test that we cannot start the tool without a verified puppetmaster
        avira.deploy.config.PUPPETMASTER_VERIFIED = "0"
        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]

        self.mox.ReplayAll()
        self.client = avira.deploy.providers.provider_cloudstack.Provider()
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.unverified_puppetmaster)
        self.mox.VerifyAll()

    @unittest.skip("Needs refactoring of config")
    def test_main_no_puppetmaster(self):
       # test that we cannot start the tool without the puppetmaster specified
        avira.deploy.config.PUPPETMASTER = ""
        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]

        self.mox.ReplayAll()
        self.client = avira.deploy.providers.provider_cloudstack.Provider()
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.no_puppetmaster)
        self.mox.VerifyAll()

    @unittest.skip("Needs refactoring of config")
    def test_main_single_line(self):
        # Mock the Cloudstack client library
        self.mock_client = self.mox.CreateMock(cloudstack.client.Client)
        self.mox.StubOutWithMock(avira.deploy.providers.provider_cloudstack,
                                 "Client")
        avira.deploy.providers.provider_cloudstack.Client("apiurl",
                                 "apikey",
                                 "secret").AndReturn(self.mock_client)

         # test the command line tool with arguments, we test the status cmd
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                         AndReturn(testdata.listVirtualMachines_output)
        self.mox.ReplayAll()
        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_status_output_running)
        self.mox.VerifyAll()

