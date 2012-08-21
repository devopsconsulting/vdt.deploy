import sys
import cloudstack
import mox
import avira.deploy.tool
import testdata
import subprocess
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
        # test the output when we don't have any userdata
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
        avira.deploy.tool.find_machine('1113',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_reboot('1113')
        output = self.out.getvalue()
        self.assertEqual(output, "machine with id 1113 is not found\n")
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

    def test_list_unknown(self):
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_list("unknown directive")
        output = self.out.getvalue()
        self.assertEqual(output, "Not implemented\n")

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

    def test_list_diskofferings(self):
        self.mock_client.listDiskOfferings().\
                        AndReturn(testdata.list_diskofferings_output)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_list("diskofferings")
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_list_diskofferings_output)
        self.mox.VerifyAll()

    def test_list_ip(self):
        self.mock_client.listPublicIpAddresses().\
                    AndReturn(testdata.list_public_ip_output)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_list("ip")
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_list_ip_output)
        self.mox.VerifyAll()

    def test_list_networks(self):
        self.mock_client.listNetworks({'zoneid': avira.deploy.tool.ZONEID}).\
                                    AndReturn(testdata.list_networks_output)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_list("networks")
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_list_networks_output)
        self.mox.VerifyAll()

    def test_list_portforwardings(self):
        domainid = avira.deploy.tool.DOMAINID
        self.mock_client.listPortForwardingRules({'domain': domainid}).\
                                AndReturn(testdata.list_portforwardings_output)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_list("portforwardings")
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_list_portforwardings_output)
        self.mox.VerifyAll()

    def test_request_unknown(self):
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_request("unknown directive")
        output = self.out.getvalue()
        self.assertEqual(output, "Not implemented\n")

    def test_request_ip(self):
        zoneid = avira.deploy.tool.ZONEID
        self.mock_client.associateIpAddress({'zoneid': zoneid}).\
                                    AndReturn({u'id': 1, u'jobid': 1})

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_request("ip")
        output = self.out.getvalue()
        self.assertEqual(output, "created ip address with id 1\n")
        self.mox.VerifyAll()

    def test_release_unknown(self):
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_release("unknown directive", "unkown value")
        output = self.out.getvalue()
        self.assertEqual(output, "Not implemented\n")

    def test_release_ip(self):
        self.mock_client.disassociateIpAddress({'id': '1'}).\
                                    AndReturn({u'jobid': 1})

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_release("ip", "1")
        output = self.out.getvalue()
        self.assertEqual(output, "releasing ip address, job id: 1\n")
        self.mox.VerifyAll()

    def test_portfw(self):
        self.mock_client.createPortForwardingRule({
                        'ipaddressid': '1',
                        'privateport': '1111',
                        'publicport': '1111',
                        'protocol': 'TCP',
                        'virtualmachineid': '1111'
                        }).AndReturn({u'id': 1, u'jobid': 1})

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_portfw("1111", "1", "1111", "1111")
        output = self.out.getvalue()
        self.assertEqual(output,
                        "added portforward for machine 1111 (1111 -> 1111)\n")
        self.mox.VerifyAll()

    def test_ssh_not_found(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine('1114',
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_ssh('1114')
        output = self.out.getvalue()
        self.assertEqual(output, "machine with id 1114 is not found\n")
        self.mox.VerifyAll()

    def test_ssh_exists(self):
        machine = StringCaster({'id': '1111'})
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mock_client.listPortForwardingRules().\
                                AndReturn(testdata.list_portforwardings_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine(machine.id,
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        self.mock_client.listPublicIpAddresses().\
                    AndReturn(testdata.list_public_ip_output)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_ssh('1111')
        output = self.out.getvalue()
        self.assertEqual(output, testdata.ssh_exists)
        self.mox.VerifyAll()

    def test_ssh(self):
        machine = StringCaster({'id': '1112'})
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mock_client.listPortForwardingRules().\
                                AndReturn(testdata.list_portforwardings_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine(machine.id,
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        self.mock_client.listPublicIpAddresses().\
                    AndReturn(testdata.list_public_ip_output)
        self.mock_client.createPortForwardingRule({
                        'ipaddressid': '1',
                        'privateport': '22',
                        'publicport': '1112',
                        'protocol': 'TCP',
                        'virtualmachineid': '1112'
                        }).AndReturn({u'id': 1, u'jobid': 1})

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_ssh('1112')
        output = self.out.getvalue()
        self.assertEqual(output,
                        "machine 1112 is now reachable (via 1.1.1.1:1112)\n")
        self.mox.VerifyAll()

    def test_kick_role(self):
        KICK_CMD = ['mco', "puppetd", "runonce", "-F", "role=test"]

        self.mox.StubOutWithMock(avira.deploy.tool, "subprocess")
        avira.deploy.tool.subprocess.check_output(KICK_CMD,
                                            stderr=subprocess.STDOUT).\
                                            AndReturn(testdata.kick_output)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_kick(role='test')
        output = self.out.getvalue()
        self.assertEqual(output, testdata.kick_output + '\n')
        self.mox.VerifyAll()

    def test_kick_exception(self):
        KICK_CMD = ['mco', "puppetd", "runonce", "-F", "role=test"]

        self.mox.StubOutWithMock(avira.deploy.tool, "subprocess")
        avira.deploy.tool.subprocess.check_output(KICK_CMD,
                    stderr=subprocess.STDOUT).\
                    AndRaise(subprocess.CalledProcessError("", ""))

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.assertRaises(subprocess.CalledProcessError,
                          self.client.do_kick,
                          role='test'
                          )
        self.mox.VerifyAll()

    def test_kick_machine_notfound(self):
        machine = StringCaster({'id': '1114', 'name': 'testmachine4'})

        self.mox.StubOutWithMock(avira.deploy.tool, "subprocess")
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine(machine.id,
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(None)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_kick(machine_id=machine.id)
        output = self.out.getvalue()
        self.assertEqual(output, "machine with id 1114 is not found\n")
        self.mox.VerifyAll()

    def test_kick_machine(self):
        machine = StringCaster({'id': '1111', 'name': 'testmachine1'})
        KICK_CMD = ['mco', "puppetd", "runonce", "-F", "hostname=testmachine1"]

        self.mox.StubOutWithMock(avira.deploy.tool, "subprocess")
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)
        self.mox.StubOutWithMock(avira.deploy.tool, "find_machine")
        avira.deploy.tool.find_machine(machine.id,
                                       testdata.listVirtualMachines_output).\
                                       AndReturn(machine)
        avira.deploy.tool.subprocess.check_output(KICK_CMD,
                                            stderr=subprocess.STDOUT).\
                                            AndReturn(testdata.kick_output)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_kick(machine_id=machine.id)
        output = self.out.getvalue()
        self.assertEqual(output, testdata.kick_output + '\n')
        self.mox.VerifyAll()

    def test_quit(self):
        # just a test to make sure this method is called
        self.mox.StubOutWithMock(avira.deploy.tool, "sys")
        avira.deploy.tool.sys.exit(0).AndReturn(None)

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.assertEqual(self.client.do_quit(), None)
        self.mox.VerifyAll()

    def test_mco(self):
        # just a test to make sure this method is called
        self.mox.StubOutWithMock(avira.deploy.tool, "check_call_with_timeout")
        avira.deploy.tool.check_call_with_timeout(['mco'], 5).\
                                    AndReturn(testdata.mco_output())

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.client.do_mco()
        output = self.out.getvalue()
        self.assertEqual(output, "mco output\n['mco']\n")
        self.mox.VerifyAll()

    def test_main_unverified_puppetmaster(self):
        self.mox.StubOutWithMock(avira.deploy.tool, "sys")
        avira.deploy.tool.sys.exit(0).AndReturn(None)
        avira.deploy.tool.PUPPETMASTER_VERIFIED = "0"
        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.unverified_puppetmaster)
        self.mox.VerifyAll()

    def test_main_no_puppetmaster(self):
        self.mox.StubOutWithMock(avira.deploy.tool, "sys")
        avira.deploy.tool.sys.exit(0).AndReturn(None)
        avira.deploy.tool.PUPPETMASTER = None
        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]

        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.no_puppetmaster)
        self.mox.VerifyAll()

    def test_main_status(self):
        self.mock_client.listVirtualMachines({'domainid': '1'}).\
                        AndReturn(testdata.listVirtualMachines_output)

        self.mox.ReplayAll()
        avira.deploy.tool.sys.argv = [avira.deploy.tool.sys.argv[0], "status"]
        avira.deploy.tool.main()
        output = self.out.getvalue()
        self.assertEqual(output, testdata.do_status_output_running)
        self.mox.VerifyAll()
