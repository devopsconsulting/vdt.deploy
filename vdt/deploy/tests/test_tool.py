import sys
import os
import cloudstack
import mox
import testdata
import unittest
from StringIO import StringIO
import mockconfig
import vdt.deploy.tool
import vdt.deploy.config


class ToolTest(unittest.TestCase):

    def setUp(self):
        reload(mockconfig)
        self.mockconfig = mockconfig.MockConfig
        vdt.deploy.tool.cfg = self.mockconfig
        self.mox = mox.Mox()
        os.environ["HOME"] = "/tmp"
        configfile = "%s/.vdtdeployment.cfg" % os.path.expanduser("~")
        vdt.deploy.tool.configfile = configfile
        vdt.deploy.config.configfile = configfile
        # this generates a system exit, we catch it now
        try:
            vdt.deploy.tool.run(gen_config='cloudstack')
        except:
            pass
        self.saved_stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out

    def tearDown(self):
        self.mox.UnsetStubs()
        sys.stdout = self.saved_stdout
        self.out = None
        if os.path.exists("/tmp/.vdtdeployment.cfg"):
            os.remove("/tmp/.vdtdeployment.cfg")

    def test_main_unverified_puppetmaster(self):
        # test that we cannot start the tool without a verified puppetmaster
        self.mockconfig.PUPPETMASTER_VERIFIED = "0"
        vdt.deploy.tool.cfg = self.mockconfig

        vdt.deploy.tool.sys.argv = [vdt.deploy.tool.sys.argv[0], "status"]
        try:
            vdt.deploy.tool.main()
        except SystemExit:
            pass
        output = self.out.getvalue()
        self.assertEqual(output, testdata.unverified_puppetmaster)

    def test_main_no_puppetmaster(self):
       # test that we cannot start the tool without the puppetmaster specified
        self.mockconfig.PUPPETMASTER = ""
        vdt.deploy.tool.cfg = self.mockconfig
        vdt.deploy.tool.sys.argv = [vdt.deploy.tool.sys.argv[0], "status"]
        try:
            vdt.deploy.tool.main()
        except SystemExit:
            pass
        output = self.out.getvalue()
        self.assertEqual(output, testdata.no_puppetmaster)

    @unittest.skip
    def test_main_single_line(self):
        # Mock the Cloudstack client library
        self.mock_client = self.mox.CreateMock(cloudstack.client.Client)
        self.mox.StubOutWithMock(vdt.deploy.providers.provider_cloudstack,
                                 "Client")
        vdt.deploy.providers.provider_cloudstack.Client("apiurl",
                                 "apikey",
                                 "secret").AndReturn(self.mock_client)

         # test the command line tool with arguments, we test the status cmd
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                         AndReturn(testdata.listVirtualMachines_output)
        self.mox.ReplayAll()
        vdt.deploy.tool.sys.argv = [vdt.deploy.tool.sys.argv[0], "status"]
        try:
            vdt.deploy.tool.main()
        except SystemExit:
            pass
        output = self.out.getvalue()
        self.assertTrue("Running" in output)
        self.mox.VerifyAll()

    def test_generate_config(self):
        # this is generated in the setup of this test
        self.assertEqual(os.path.isfile("/tmp/.vdtdeployment.cfg"), True)
        # import something from config, it should have read it from the
        # generated configfile
        from vdt.deploy.config import Config
        cfg = Config()
        print cfg.PUPPETMASTER
        self.assertEqual(cfg.PUPPETMASTER, "")
