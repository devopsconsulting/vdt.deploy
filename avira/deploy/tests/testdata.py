#PEP8 --ignore=E501
listVirtualMachines_output = [{u'domain': u'Virtual Deployment Team', u'domainid': 1, u'haenable': False, u'templatename': u'VDT Base 0.5', u'securitygroup': [], u'zoneid': 1, u'cpunumber': 2, u'passwordenabled': False, u'id': 1111, u'cpuused': u'0.09%', u'state': u'Running', u'guestosid': 100, u'networkkbswrite': 285241, u'memory': 5120, u'serviceofferingid': 17, u'zonename': u'Z2-DTC1', u'displayname': u'testmachine1', u'nic': [{u'networkid': 307, u'macaddress': u'02:00:4c:c2:00:cb', u'type': u'Virtual', u'gateway': u'172.31.8.1', u'traffictype': u'Guest', u'netmask': u'255.255.255.0', u'ipaddress': u'172.31.8.164', u'id': 8346, u'isdefault': True}], u'cpuspeed': 3468, u'templateid': 392, u'account': u'vdt.admin', u'name': u'i-42-1111-VM', u'networkkbsread': 372302, u'created': u'2012-07-25T07:39:53+0000', u'hypervisor': u'KVM', u'rootdevicetype': u'NetworkFilesystem', u'rootdeviceid': 0, u'serviceofferingname': u'Small', u'templatedisplaytext': u'VDT Base 0.5'},
                              {u'domain': u'Virtual Deployment Team', u'domainid': 1, u'haenable': False, u'templatename': u'VDT Base 0.5', u'securitygroup': [], u'zoneid': 1, u'cpunumber': 2, u'passwordenabled': False, u'id': 1112, u'cpuused': u'0.09%', u'state': u'Stopped', u'guestosid': 100, u'networkkbswrite': 285241, u'memory': 5120, u'serviceofferingid': 17, u'zonename': u'Z2-DTC1', u'displayname': u'testmachine2', u'nic': [{u'networkid': 307, u'macaddress': u'02:00:4c:c2:00:ce', u'type': u'Virtual', u'gateway': u'172.31.8.1', u'traffictype': u'Guest', u'netmask': u'255.255.255.0', u'ipaddress': u'172.31.8.165', u'id': 8346, u'isdefault': True}], u'cpuspeed': 3468, u'templateid': 392, u'account': u'vdt.admin', u'name': u'i-42-1112-VM', u'networkkbsread': 372302, u'created': u'2012-07-25T07:39:53+0000', u'hypervisor': u'KVM', u'rootdevicetype': u'NetworkFilesystem', u'rootdeviceid': 0, u'serviceofferingname': u'Small', u'templatedisplaytext': u'VDT Base 0.5'}]
do_status_output_running = "                  testmachine1    i-42-1111-VM  1111  Running\n"
do_status_output_all = "                  testmachine1    i-42-1111-VM  1111  Running\n                  testmachine2    i-42-1112-VM  1112  Stopped\n"
do_deploy_no_userdata = "Specify the machine userdata, (at least it's role)\n"
do_deploy_duplicate = "A machine with the name testmachine1 already exists\n"
do_deploy_output = "testmachine3 started, machine id 1113\n"


def run_machine_cleanup_output():
    print """
Determining the amount of hosts matching filter for 2 seconds .... 1

 * [ ==========================================================> ] 1 / 1


i-42-1112-VM                            : OK
    {:status=>0,     :err=>"",     :out=>"no cleaner found for testmachine2, doing nothing."}



---- cleanup#cleanup call stats ----
           Nodes: 1 / 1
     Pass / Fail: 1 / 0
      Start Time: Mon Aug 20 14:37:53 +0200 2012
  Discovery Time: 2003.62ms
      Agent Time: 120.09ms
      Total Time: 2123.70ms"""


def remove_machine_port_forwards_output():
    print """
Removing portforward 10.120.137.186:1112 -> 22
Removing portforward 10.120.137.196:1112 -> 22
"""


def node_clean_output():
    print """
notice: Revoked certificate with serial 30
notice: Removing file Puppet::SSL::Certificate i-42-1112-vm.cs2acloud.internal at '/var/lib/puppet/ssl/ca/signed/i-42-1112-vm.cs2acloud.internal.pem'
notice: Removing file Puppet::SSL::Certificate i-42-1112-vm.cs2acloud.internal at '/var/lib/puppet/ssl/certs/i-42-1112-vm.cs2acloud.internal.pem'
notice: Force i-42-1112-vm.cs2acloud.internal's exported resources to absent
warning: Please wait until all other hosts have checked out their configuration before finishing the cleanup with:
warning: $ puppet node clean i-42-1112-vm.cs2acloud.internal
["i-42-1112-vm.cs2acloud.internal"]

notice: Revoked certificate with serial 30
notice: i-42-1112-vm.cs2acloud.internal storeconfigs removed
["i-42-1112-vm.cs2acloud.internal"]"""

clean_foreman_output_data = """
/usr/share/foreman/vendor/ruby/1.8/gems/ruby_parser-2.3.1/lib/ruby_parser_extras.rb:10: warning: already initialized constant ENC_NONE
/usr/share/foreman/vendor/ruby/1.8/gems/ruby_parser-2.3.1/lib/ruby_parser_extras.rb:11: warning: already initialized constant ENC_EUC
/usr/share/foreman/vendor/ruby/1.8/gems/ruby_parser-2.3.1/lib/ruby_parser_extras.rb:12: warning: already initialized constant ENC_SJIS
/usr/share/foreman/vendor/ruby/1.8/gems/ruby_parser-2.3.1/lib/ruby_parser_extras.rb:13: warning: already initialized constant ENC_UTF8

All out of sync hosts exists in DNS"""


def clean_foreman_output():
    print clean_foreman_output_data
