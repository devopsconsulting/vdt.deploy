import os
from unittest import TestCase


class DeployConfigTest(TestCase):
    def setUp(self):
        # we set the home directory to /tmp for the test
        os.environ["HOME"] = "/tmp"
        import avira.deploy.config
        avira.deploy.config

    def tearDown(self):
        if os.path.exists("/tmp/.aviradeployment.cfg"):
            os.remove("/tmp/.aviradeployment.cfg")

    def test_generate_config(self):
        # when we import the module it should generate a configfile in
        # our home directory
        self.assertEqual(os.path.isfile("/tmp/.aviradeployment.cfg"), True)
        # import something from config, it should have read it from the
        # generated configfile
        from avira.deploy.config import PUPPETMASTER
        self.assertEqual(PUPPETMASTER, "")
