from unittest import TestCase
import cloudstack
import mox
import avira.deploy
import avira.deploy.tool


class DeployToolTest(TestCase):
    def setUp(self):
        self.mox = mox.Mox()
        mock_client = self.mox.CreateMock(cloudstack.client.Client)
        self.mox.StubOutWithMock(avira.deploy.tool, "Client")
        avira.deploy.tool.Client("apiurl",
                                 "apikey",
                                 "secret").AndReturn(mock_client)
        avira.deploy.tool.APIURL = "apiurl"
        avira.deploy.tool.APIKEY = "apikey"
        avira.deploy.tool.SECRETKEY = "secret"

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_do_status(self):
        # we should have no VM's add the moment
        self.mox.ReplayAll()
        self.client = avira.deploy.tool.CloudstackDeployment()
        self.mox.VerifyAll()
