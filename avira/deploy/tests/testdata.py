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

list_zones_output = [{u'name': u'Testzone', u'zonetoken': u'11111111-d585-36a5-a7c3-5af1de99a069', u'securitygroupsenabled': False, u'allocationstate': u'Enabled', u'dhcpprovider': u'VirtualRouter', u'networktype': u'Advanced', u'id': 1}]
list_templates_output = [{u'domain': u'Testdomain', u'domainid': 1, u'zoneid': 1, u'displaytext': u'Cloud Ubuntu OneIric v3 (Z2-DTC1)', u'ostypeid': 1, u'passwordenabled': True, u'id': 1, u'size': 107374182400, u'isready': True, u'templatetype': u'USER', u'zonename': u'Testzone', u'status': u'Download Complete', u'ostypename': u'Ubuntu (64-bit)', u'format': u'QCOW2', u'isfeatured': False, u'isextractable': False, u'crossZones': False, u'account': u'Testaccount', u'name': u'Cloud Ubuntu OneIric v3', u'created': u'2012-01-25T09:39:00+0000', u'hypervisor': u'KVM', u'ispublic': True}]
do_list_templates_output = "    1                    Cloud Ubuntu OneIric v3   Testzone\n"

list_serviceofferings_output = [{u'name': u'Extra Medium', u'created': u'2012-08-09T07:35:29+0000', u'storagetype': u'shared', u'limitcpuuse': False, u'cpuspeed': 3466, u'offerha': False, u'cpunumber': 6, u'memory': 16384, u'displaytext': u'6x 3.47GHZ, 16 GB Mem', u'issystem': False, u'id': 1, u'defaultuse': False}]
do_list_serviceofferings_output = "    1    6x 3.47GHZ, 16 GB Mem\n"

list_diskofferings_output = [{u'iscustomized': False, u'name': u'Medium 50GB', u'created': u'2011-09-20T11:51:30+0000', u'disksize': 50, u'displaytext': u'Medium 50GB', u'id': 1}]
do_list_diskofferings_output = "    1                      Medium 50GB    50 GB\n"

list_public_ip_output = {u'count': 2, u'publicipaddress': [{u'networkid': 1, u'account': u'account', u'domainid': 1, u'issourcenat': True, u'isstaticnat': False, u'domain': u'Test Domain', u'zoneid': 1, u'state': u'Allocated', u'associatednetworkid': 1, u'forvirtualnetwork': True, u'allocated': u'2012-03-09T13:14:26+0000', u'ipaddress': u'1.1.1.1', u'id': 1, u'zonename': u'Testzone'}]}
do_list_ip_output = "    1           1.1.1.1\n"

list_networks_output = [{u'related': 1, u'zoneid': 1, u'displaytext': u'Test network', u'id': 1, u'networkdomain': u'network domain', u'service': [{u'capability': [{u'name': u'SupportedProtocols', u'value': u'tcp, udp'}, {u'name': u'SupportedLbAlgorithms', u'value': u'roundrobin,leastconn,source'}], u'name': u'Lb'}, {u'capability': [{u'name': u'AllowDnsSuffixModification', u'value': u'true'}], u'name': u'Dns'}, {u'name': u'Dhcp'}, {u'name': u'UserData'}], u'securitygroupenabled': False, u'gateway': u'1.1.1.1', u'state': u'Setup', u'isdefault': False, u'type': u'Direct', u'broadcasturi': u'vlan://1111', u'networkofferingavailability': u'Optional', u'networkofferingid': 1, u'vlan': u'1', u'networkofferingdisplaytext': u'Direct', u'traffictype': u'Guest', u'netmask': u'255.255.255.0', u'broadcastdomaintype': u'Vlan', u'isshared': True, u'endip': u'1.1.1.2', u'name': u'testnetwork', u'startip': u'1.1.1.1', u'dns2': u'3.3.3.3', u'dns1': u'2.2.2.2', u'networkofferingname': u'DefaultDirectNetworkOffering', u'issystem': False}]
do_list_networks_output = "    1       testnetwork\n"

list_portforwardings_output = [{u'protocol': u'tcp', u'virtualmachineid': 1111, u'ipaddress': u'1.1.1.1', u'cidrlist': '', u'ipaddressid': 1, u'virtualmachinedisplayname': u'testserver1', u'privateendport': u'22', u'state': u'Active', u'publicendport': u'1111', u'privateport': u'22', u'virtualmachinename': u'i-42-1111-VM', u'publicport': u'1111', u'id': 1}]
do_list_portforwardings_output = "    1           1.1.1.1    1111 to    22  on machine  1111-testserver1\n"

ssh_exists = "machine 1111 already has a ssh portforward with ip 1.1.1.1\n"

kick_output = """

1 / 1




Finished processing 1 / 1 hosts in 78.63 ms

"""

unverified_puppetmaster = "\nPlease edit your configfile : \n\nSet puppetmaster_verified to 1 if you are sure you run this deployment tool on the puppetmaster.\n"
no_puppetmaster = "Please specify the fqdn of the puppetmaster in the config\n"