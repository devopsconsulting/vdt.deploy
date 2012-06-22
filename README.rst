avira.deploy
============

avira.deployment provides a command line tool for deploying VM's in Cloudstack
with a puppet role. The puppet role defines the installation and configuration
of the server. For example a server with the role *lvs* will be installed and
configured as an lvs load balancer.

Deployment of a server is a 3 phase process.

1. Create vm with cloudstack api.
2. Boot vm and run `cloud-init <https://code.launchpad.net/cloud-init>`_ to
   initialize the base ubuntu installation. cloud-init will also install
   puppet.
3. puppet will start and choose the correct manifests based on the puppet
   role. Puppet will install and configure the machine and register with
   the load balancer.

.. index:: Configuration, avira.deploy; configuration

.. _avira-deploy-configuration:

Configuration
+++++++++++++

avira.deploy uses a configuration file located at::

    ~/.aviradeployment.cfg

Initially avira.deploy will create this file for you but not configured yet:

.. code-block:: ini

    [deployment]
    apiurl = http://mgmt1-dtc1.avira-cloud.net:8080/client/api
    apikey = 
    secretkey = 
    domainid = 29
    zoneid = 6
    templateid = 392
    serviceid = 17
    cloudinit_puppet = http://joe.avira-cloud.net/autodeploy/vdt-puppet-agent.cloudinit
    cloudinit_base = http://joe.avira-cloud.net/autodeploy/vdt-base.cloudinit


You've got to enter your cloudstack apikey and secretkey. Options are::

    apiurl:           The full url of the cloudstack api in your domain.
    apikey:           The api key of your cloudstack domain.
    secretkey:        The secretkey of your cloudstack domain.
    domainid:         The numeric id of your domain.
    zoneid:           The numeric id of the zone your domain belongs to.
    templateid:       The id of the vm template with your base installation.
    serviceid:        Sorry no idea.
    cloudinit_puppet: The cloud-init configuration for installations that are
                      completed using puppet.
    cloudinit_base:   The cloud-init configuration for installations that are
                      need to be completed manually (eg. puppetmaster)

.. index:: Usage, avira.deploy; usage

.. _avira-deploy-usage:

Usage
+++++

Now that avira.deploy is configured to use the proper coudstack domain, it is
ready for use. avira.deploy can run in both single command as interactive mode.

Let's start with interactive mode::
    
    python deploy.py
    deploy> 
    deploy> help
    
    Documented commands (type help <topic>):
    ========================================
    deploy   kick  quit    release  ssh    status
    destroy  list  reboot  request  start  stop  
    
    Undocumented commands:
    ======================
    help
    
    deploy>

.. index::
    single: avira.deploy; help

.. _avira-deploy-help:

Typing ``help`` shows you all available commands. typing::

    deploy> help <commandname>

shows you what a command does and what parameters it requires::

    deploy> help status

            Shows running instances, specify 'all' to show all instances

            Usage::

                deploy> status [all]

    deploy>

So status will show you the running instances.

.. _avira-deploy-commands:

.. index::
    single: avira.deploy; deploy
    single: avira.deploy; destroy
    single: avira.deploy; kick
    single: avira.deploy; list
    single: avira.deploy; quit
    single: avira.deploy; release
    single: avira.deploy; request
    single: avira.deploy; ssh
    single: avira.deploy; start
    single: avira.deploy; status
    single: avira.deploy; reboot

The help for each command is shown below, but the names of the commands are
prefixed with 'do'. (Not in github readme).
    
.. automethod:: deploy.CloudstackDeployment.do_deploy(name, userdata=None, cloudinit_config=CLOUDINIT_PUPPET)

.. automethod:: deploy.CloudstackDeployment.do_destroy(machine_id)

.. automethod:: deploy.CloudstackDeployment.do_kick(machine_id)

.. automethod:: deploy.CloudstackDeployment.do_list(type="templates or diskofferings or ip")

.. automethod:: deploy.CloudstackDeployment.do_quit()

.. automethod:: deploy.CloudstackDeployment.do_release(type)

.. automethod:: deploy.CloudstackDeployment.do_request(type)

.. automethod:: deploy.CloudstackDeployment.do_ssh(machine_id)

.. automethod:: deploy.CloudstackDeployment.do_stop(machine_id)

.. automethod:: deploy.CloudstackDeployment.do_start(machine_id)

.. automethod:: deploy.CloudstackDeployment.do_status(all=False)

.. automethod:: deploy.CloudstackDeployment.do_reboot(machine_id)
