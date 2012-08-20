import sys
import cloudstack
import mox
import avira.deploy.tool
import testdata
from unittest import TestCase
from StringIO import StringIO
from base64 import encodestring
from avira.deploy.utils import StringCaster


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
        avira.deploy.tool.find_machine('1114',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_destroy('1114')
        output = self.out.getvalue()
        self.assertEqual(output, "No machine found with the id 1114\n")
        self.mox.VerifyAll()

    def test_do_destroy_puppetmaster(self):
        machine = StringCaster({'id': '1112', 'name': 'testmachine2'})
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine(machine.id,
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        self.mox.StubOutWithMock(avira.deploy.tool, "is_puppetmaster")
        avira.deploy.tool.is_puppetmaster(machine.id).AndReturn(True)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_destroy(machine.id)
        output = self.out.getvalue()
        self.assertEqual(output,
                         "You are not allowed to destroy the puppetmaster\n")
        self.mox.VerifyAll()

    def test_do_destroy(self):
        machine = StringCaster({'id': '1112', 'name': 'testmachine2'})
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine(machine.id,
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        self.mox.StubOutWithMock(avira.deploy.tool, "is_puppetmaster")
        avira.deploy.tool.is_puppetmaster(machine.id).AndReturn(False)
        self.mox.StubOutWithMock(avira.deploy.tool, "run_machine_cleanup")
        avira.deploy.tool.run_machine_cleanup(machine).\
                            AndReturn(testdata.run_machine_cleanup_output())

        self.mock_client.destroyVirtualMachine({'id': machine.id}).\
                        AndReturn("Destroying machine with id %s" % machine.id)
        self.mox.StubOutWithMock(avira.deploy.tool,
                                 "remove_machine_port_forwards")

        avira.deploy.tool.remove_machine_port_forwards(machine,
                    self.mock_client).\
                    AndReturn(testdata.remove_machine_port_forwards_output())
        self.mox.StubOutWithMock(avira.deploy.tool, "node_clean")
        avira.deploy.tool.node_clean(machine).\
                                        AndReturn(testdata.node_clean_output())
        self.mox.StubOutWithMock(avira.deploy.tool, "clean_foreman")
        avira.deploy.tool.clean_foreman().\
                                    AndReturn(testdata.clean_foreman_output())

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_destroy(machine.id)
        output = self.out.getvalue()
        self.assertTrue(output,
            "Determining the amount of hosts matching filter" in output)
        self.assertTrue(output,
            "Removing portforward 10.120.137.186:1112 -> 22" in output)
        self.assertTrue(output,
            "notice: Revoked certificate with serial 30" in output)
        self.assertTrue(output,
            "All out of sync hosts exists in DNS" in output)
        self.assertTrue(output,
                        "running cleanup job on testmachine2" in output)
        self.assertTrue(output,
                        "destroying machine with id 1112" in output)
        self.assertTrue(output, "running puppet node clean" in output)
        self.mox.VerifyAll()

    def test_do_clean(self):
        self.mox.StubOutWithMock(avira.deploy.tool, "clean_foreman")
        avira.deploy.tool.clean_foreman().\
                                    AndReturn(testdata.clean_foreman_output())
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_clean()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.clean_foreman_output_data + '\n')
        self.mox.VerifyAll()

    def test_do_start_not_found(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine('1114',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_start('1114')
        output = self.out.getvalue()
        self.assertEqual(output, "machine with id 1114 is not found\n")
        self.mox.VerifyAll()

    def test_do_start(self):
        machine = StringCaster({'id': '1112'})
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mock_client.startVirtualMachine(machine).\
                        AndReturn({u'jobid': 1})

        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine('1112',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_start('1112')
        output = self.out.getvalue()
        self.assertEqual(output, "starting machine with id 1112\n")
        self.mox.VerifyAll()

    def test_do_stop_not_found(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine('1114',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_stop('1114')
        output = self.out.getvalue()
        self.assertEqual(output, "machine with id 1114 is not found\n")
        self.mox.VerifyAll()

    def test_do_stop(self):
        machine = StringCaster({'id': '1111'})
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mock_client.stopVirtualMachine(machine).\
                        AndReturn({u'jobid': 1})

        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine('1111',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_stop('1111')
        output = self.out.getvalue()
        self.assertEqual(output, "stopping machine with id 1111\n")
        self.mox.VerifyAll()

    def test_do_reboot_not_found(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine('1111',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_stop('1111')
        output = self.out.getvalue()
        self.assertEqual(output, "machine with id 1111 is not found\n")
        self.mox.VerifyAll()

    def test_do_reboot(self):
        machine = StringCaster({'id': '1111'})
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mock_client.rebootVirtualMachine(machine).\
                        AndReturn({u'jobid': 1})

        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine('1111',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_reboot('1111')
        output = self.out.getvalue()
        self.assertEqual(output, "rebooting machine with id 1111\n")
        self.mox.VerifyAll()

    def test_list_templates(self):
        self.mock_client.listZones({}).AndReturn(testdata.list_zones_output)
        self.mock_client.listTemplates({
                            "templatefilter": "executable"
                        }).AndReturn(testdata.list_templates_output)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_list("templates")
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_list_templates_output)
        self.mox.VerifyAll()

    def test_list_serviceofferings(self):
        self.mock_client.listServiceOfferings().\
                        AndReturn(testdata.list_serviceofferings_output)
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_list("serviceofferings")
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_list_serviceofferings_output)
        self.mox.VerifyAll()

