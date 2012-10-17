import os
from unittest import TestCase
import avira.deploy.tool


class DeployConfigTest(TestCase):

    def setUp(self):
        # when we import the module it should generate a configfile in
        # our home directory
        # we set the home directory to /tmp for the test
        os.environ["HOME"] = "/tmp"
        configfile = "%s/.aviradeployment.cfg" % os.path.expanduser("~")
        avira.deploy.tool.configfile = configfile
        avira.deploy.config.configfile = configfile
        # first create a cloudstack configfile
        avira.deploy.tool.sys.argv = ["avira-deploy",
                                      "init",
                                      "cloudstack"]
        # this generates a system exit, we catch it now
        try:
            avira.deploy.tool.main()
        except:
            pass

    def tearDown(self):
        if os.path.exists("/tmp/.aviradeployment.cfg"):
            os.remove("/tmp/.aviradeployment.cfg")

    def test_generate_config(self):
        self.assertEqual(os.path.isfile("/tmp/.aviradeployment.cfg"), True)
        # import something from config, it should have read it from the
        # generated configfile
        from avira.deploy.config import Config
        cfg = Config()
        print cfg.PUPPETMASTER
        self.assertEqual(cfg.PUPPETMASTER, "")
