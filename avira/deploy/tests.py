from unittest import TestCase
from cloudstack.client import Client
from avira.deploy import tool
import mox


class DeployToolTest(TestCase):
    def setUp(self):
        self.mox = mox.Mox()
        from pdb import set_trace; set_trace()
        self.deploy = tool.CloudstackDeployment()
        self.deploy.client = MockCloudStack()
    

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_do_status(self):
        pass
