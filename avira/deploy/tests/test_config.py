import os
from unittest import TestCase


class DeployConfigTest(TestCase):

    def setUp(self):
        # when we import the module it should generate a configfile in
        # our home directory
        # we set the home directory to /tmp for the test
        os.environ["HOME"] = "/tmp"
        import avira.deploy.config
        avira.deploy.config.init("cloudstack")
        reload(avira.deploy.config)

    def tearDown(self):
        if os.path.exists("/tmp/.aviradeployment.cfg"):
            os.remove("/tmp/.aviradeployment.cfg")

    def test_generate_config(self):
        self.assertEqual(os.path.isfile("/tmp/.aviradeployment.cfg"), True)
        # import something from config, it should have read it from the
        # generated configfile
        from avira.deploy.config import PUPPETMASTER
        print PUPPETMASTER
        self.assertEqual(PUPPETMASTER, "")
