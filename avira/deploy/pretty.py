def machine_print(machines):
    for machine in machines:
        print "%(displayname)30s %(name)15s %(id)5s  %(state)s" % machine


def serviceofferings_print(serviceofferings):
    for serviceoffering in serviceofferings:
        print "%(id)5s    %(displaytext)s" % serviceoffering

def templates_print(templates, zones):
    for template in templates:
        template['zone'] = zones.get(template['zoneid'], 'zone unknown')
        print "%(id)5s   %(name)40s   %(zone)s" % template

def diskofferings_print(diskofferings):
    for diskoffering in diskofferings:
        print "%(id)5s   %(name)30s %(disksize)5s GB" % diskoffering

def public_ipaddresses_print(ipaddresses):
    for ipaddress in ipaddresses['publicipaddress']:
        print "%(id)5s   %(ipaddress)15s" % ipaddress

def networks_print(networks):
    for network in networks:
        print "%(id)5s   %(name)15s" % network

def portforwardings_print(portforwardings):
    for portforwarding in portforwardings:
        print "%(id)5s   %(ipaddress)15s   %(publicport)4s to %(privateport)4s" \
              " on machine %(virtualmachineid)5s-%(virtualmachinedisplayname)s" \
                % portforwarding