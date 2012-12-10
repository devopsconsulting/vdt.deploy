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
    puppetmaster = 
    puppetmaster_verified = 0
    cleanup_timeout = 20

You've got to enter your cloudstack apikey and secretkey. Options are::

    apiurl:                 The full url of the cloudstack api in your domain.
    apikey:                 The api key of your cloudstack domain.
    secretkey:              The secretkey of your cloudstack domain.
    domainid:               The numeric id of your domain.
    zoneid:                 The numeric id of the zone your domain belongs to.
    templateid:             The id of the vm template with your base installation.
    serviceid:              The service offering id. Default it will be a small
                            installation. (2 cores, 5 GB of RAM)
    cloudinit_puppet:       The cloud-init configuration for installations that are
                            completed using a puppet agent.
    cloudinit_base:         The cloud-init configuration for installations that are
                            need to be completed manually (eg. puppetmaster)
    puppetmaster:           The FQDN of the puppetmaster. This will be passed as
                            userdata to the deployed machines so they can find the
                            puppetmaster.
    puppetmaster_verified:  Defaults to zero and should be set to 1 if you are sure
                            you run the deployment tool on the puppetmaster
    cleanup_timeout:        If a host requires cleanup to run before destroying,
                            only wait cleanup_timeout seconds before continuing
                            the destruction process.

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
    deploy   kick  portfw  reboot   request  start   stop
    destroy  list  quit    release  ssh      status    

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
    single: avira.deploy; status
    single: avira.deploy; deploy
    single: avira.deploy; destroy
    single: avira.deploy; start
    single: avira.deploy; stop
    single: avira.deploy; reboot
    single: avira.deploy; list
    single: avira.deploy; request
    single: avira.deploy; release
    single: avira.deploy; portfw
    single: avira.deploy; ssh
    single: avira.deploy; kick
    single: avira.deploy; quit
	single: avira.deploy; mco

The help for each command is shown below, but the names of the commands are
prefixed with 'do'. (Not in github readme).

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_status

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_deploy

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_start

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_stop

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_reboot

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_destroy

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_list

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_request

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_release

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_portfw

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_ssh

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_kick

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_quit

.. automethod:: avira.deployplugin.cloudstack.provider.Provider.do_mco

Override settings from the command line
+++++++++++++++++++++++++++++++++++++++

Most of the stuff in the settings file can be overridden per
session or per command with a flag. Here is the output of
avira-deploy -h which let's you know how it works::

    usage: avira-deploy [-h] [--gen-config GEN_CONFIG] [--provider PROVIDER]
                   [--puppetmaster PUPPETMASTER]
                   [--verified PUPPETMASTER_VERIFIED]
                   [--cleanup-timeout CLEANUP_TIMEOUT] [--apiurl APIURL]
                   [--apikey APIKEY] [--secretkey SECRETKEY] [--domainid DOMAINID]
                   [--templateid TEMPLATEID] [--serviceid SERVICEID]
                   [--cloudinit CLOUDINIT_PUPPET]
                   [command [command ...]]

    Deployment tool for deploying VM's with puppet

    positional arguments:
      command               the command to run.

    optional arguments:
      -h, --help            show this help message and exit
      --gen-config GEN_CONFIG
                            Generate a config file at ~/.aviradeployment.cfg for
                            the specified provider.
      --provider PROVIDER   Override provider.
      --puppetmaster PUPPETMASTER
                            Override puppetmaster.
      --verified PUPPETMASTER_VERIFIED
                            Override the puppetmaster verified flag.
      --cleanup-timeout CLEANUP_TIMEOUT
                            Override the mcollective cleanup timeout. (runs when
                            destroying a VM)
      --apiurl APIURL       Override the api url.
      --apikey APIKEY       Override the api key.
      --secretkey SECRETKEY
                            Override the secret key.
      --domainid DOMAINID   Override the domain.
      --templateid TEMPLATEID
                            Override the template.
      --serviceid SERVICEID
                            Override the service offering.
      --cloudinit CLOUDINIT_PUPPET
                            Override the cloudinit file.

