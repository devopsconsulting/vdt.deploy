import sys
import cloudstack
import mox
import testdata
import unittest
from StringIO import StringIO
#import avira.deploy.providers.provider_cloudstack
from mockconfig import MockConfig
import avira.deploy.tool
import avira.deploy.config


class ProviderCloudstackTest(unittest.TestCase):

    def setUp(self):
        self.saved_stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()
        sys.stdout = self.saved_stdout
        self.out = None

    def test_main_unverified_puppetmaster(self):
        # test that we cannot start the tool without a verified puppetmaster
        MockConfig.PUPPETMASTER_VERIFIED = "0"
        avira.deploy.tool.cfg = MockConfig

        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.unverified_puppetmaster)

    def test_main_no_puppetmaster(self):
       # test that we cannot start the tool without the puppetmaster specified
        MockConfig.PUPPETMASTER = ""
        avira.deploy.tool.cfg = MockConfig
        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.no_puppetmaster)

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
