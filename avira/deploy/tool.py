#! /usr/bin/python
import sys
import os
import argparse

from avira.deploy.config import cfg, configfile, main_template
from avira.deploy.utils import load_plugin_by_name, UnknownPlugin

def main(command=False, gen_config=False):
    if gen_config:
        try:
            provider_plugin = load_plugin_by_name(gen_config)
            with open(configfile, "w") as f:
                f.write(main_template)
                f.write(provider_plugin.template)
                f.close()
            print "Please edit your config at %s and restat the puppetbot if needed" % configfile
        except UnknowPlugin as e:
            print e.message
        exit(0)

    if not os.path.isfile(configfile):
        print "Please run avira-deploy --gen-config=<provider> first\n"
        sys.exit(0)

    if not cfg.PUPPETMASTER_VERIFIED == '1':
        print "Set puppetmaster_verified to 1 if you are sure you run this " \
              "deployment tool on the puppetmaster."
    elif not cfg.PUPPETMASTER:
        print "Please specify the fqdn of the puppetmaster in the config"
    else:
        try:
            provider = load_plugin_by_name(cfg.PROVIDER)
            deploy = provider.Provider()
            if command:
                line = " ".join(command)
                deploy.onecmd(line)
            else:
                try:
                    deploy.cmdloop()
                except KeyboardInterrupt:
                    deploy.do_quit('now')
        except UnknowPlugin as e:
            print e.message
            exit(1)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="Deployment tool for deploying VM's with puppet")
    p.add_argument("command", default=False, nargs='*', help="the command to run.")
    p.add_argument("--gen-config", default=False,
                   help="Generate a config file at ~/.aviradeployment.cfg for the specified provider.")

    args = p.parse_args()

    main(args.command, args.gen_config)
