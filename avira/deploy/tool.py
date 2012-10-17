#! /usr/bin/python
import sys
import os
from config import cfg, configfile, main_template


def main():
    if len(sys.argv) == 3:
        if sys.argv[1] == "init":
            exec("from providers.config_%s import template" % sys.argv[2])
            with open(configfile, "w") as f:
                f.write(main_template)
                f.write(template)
                f.close()
            print "Please edit your config at %s" % configfile
            sys.exit(0)

    if not os.path.isfile(configfile):
        print "Please run avira-deploy init <provider> first\n"
        sys.exit(0)

    if not cfg.PUPPETMASTER_VERIFIED == '1':
        print "Set puppetmaster_verified to 1 if you are sure you run this " \
              "deployment tool on the puppetmaster."
    elif not cfg.PUPPETMASTER:
        print "Please specify the fqdn of the puppetmaster in the config"
    else:
        exec("from providers.provider_%s import Provider" % cfg.PROVIDER)
        deploy = Provider()
        if len(sys.argv) > 1:
            line = " ".join(sys.argv[1:])
            deploy.onecmd(line)
        else:
            try:
                deploy.cmdloop()
            except KeyboardInterrupt:
                deploy.do_quit('now')


if __name__ == '__main__':
    main()
