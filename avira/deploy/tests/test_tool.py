import sys
import cloudstack
import mox
import avira.deploy.tool
import testdata
from unittest import TestCase
from StringIO import StringIO
from base64 import encodestring


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
        avira.deploy.tool.SERVICEID = "1"
        avira.deploy.tool.TEMPLATEID = "1"
        avira.deploy.tool.ZONEID = "1"
        avira.deploy.tool.DOMAINID = "1"
        avira.deploy.tool.PUPPETMASTER = "localhost"
        avira.deploy.tool.CLOUDINIT_PUPPET = \
                "http://localhost/autodeploy/vdt-puppet-agent.cloudinit"
        self.sample_userdata = "#include %s\n#puppetmaster=%s\n" % \
                                        (avira.deploy.tool.CLOUDINIT_PUPPET,
                                         avira.deploy.tool.PUPPETMASTER)

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

    def test_do_deploy_duplicate_machine(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_deploy("testmachine1", userdata={'role': 'test'})
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_deploy_duplicate)
        self.mox.VerifyAll()

    def test_do_deploy(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)

        userdata = self.sample_userdata + "#userdata={'role': 'test'}\n"
        userdata = encodestring(userdata)
        result = {u'id': 1113, u'jobid': 1}
        self.mock_client.deployVirtualMachine({'domainid': '1',
                                               'userdata': userdata,
                                               'networkids': '',
                                               'domainid': '1',
                                               'displayname': 'testmachine3',
                                               'zoneid': '1',
                                               'templateid': '1',
                                               'serviceofferingid': '1'}
                                               ).AndReturn(result)
        self.mox.StubOutWithMock(avira.deploy.tool, "add_pending_certificate")
        avira.deploy.tool.add_pending_certificate(1113).\
                                                    AndReturn(None)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_deploy("testmachine3", userdata={'role': 'test'})
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_deploy_output)
        self.mox.VerifyAll()

    def test_do_destroy_no_exists(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine(1114,
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_destroy(1114)
        output = self.out.getvalue()
        self.assertEqual(output, "No machine found with the id 1114\n")
        self.mox.VerifyAll()
