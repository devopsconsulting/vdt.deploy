#! /usr/bin/python
import sys
import os
from config import init


def main():
    if len(sys.argv) == 3:
        if sys.argv[1] == "init":
            init(sys.argv[2])
            print "Please edit your config at %s/.aviradeployment.cfg" % \
                                                        os.path.expanduser("~")
    configfile = "%s/.aviradeployment.cfg" % os.path.expanduser("~")
    if not os.path.isfile(configfile):
        print "Please run avira-deploy init <cloudstack|vagrant> first\n"
        exit(0)

    from config import PUPPETMASTER_VERIFIED, PUPPETMASTER, PROVIDER
    if not PUPPETMASTER_VERIFIED == '1':
        print "Set puppetmaster_verified to 1 if you are sure you run this " \
              "deployment tool on the puppetmaster."
    elif not PUPPETMASTER:
        print "Please specify the fqdn of the puppetmaster in the config"
    else:
        exec("from providers.provider_%s import Provider" %  PROVIDER)
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
