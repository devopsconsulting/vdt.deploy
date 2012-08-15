import sys
import cloudstack
import mox
import avira.deploy.tool
import testdata
from unittest import TestCase
from StringIO import StringIO


class DeployToolTest(TestCase):

    def setUp(self):
        self.saved_stdout = sys.stdout
        self.out = StringIO()
        sys.stdout = self.out

        self.mox = mox.Mox()
        self.mock_client = self.mox.CreateMock(cloudstack.client.Client)
        self.mox.StubOutWithMock(avira.deploy.tool, "Client")
        avira.deploy.tool.Client("apiurl",
                                 "apikey",
                                 "secret").AndReturn(self.mock_client)
        avira.deploy.tool.APIURL = "apiurl"
        avira.deploy.tool.APIKEY = "apikey"
        avira.deploy.tool.SECRETKEY = "secret"
        avira.deploy.tool.DOMAINID = "1"

    def tearDown(self):
        self.mox.UnsetStubs()
        sys.stdout = self.saved_stdout
        self.out = None

    def test_do_status(self):
        # we have two vm's, one is running one is stopped.
        # we should only display the running one as we normally filter
        # on running machines
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_status()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_status_output_running)
        self.mox.VerifyAll()

    def test_do_status_all(self):
        # now we should have two vm's, as we specify 'all'
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_status(all=True)
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_status_output_all)
        self.mox.VerifyAll()

    def test_do_deploy_no_userdata(self):
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_deploy("test")
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_deploy_no_userdata)
