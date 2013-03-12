import os
from unittest import TestCase
import mox
import vdt.deploy.utils
import vdt.deploy.certificate
import mockconfig


class DeployUtilsTest(TestCase):

    def setUp(self):
        self.mox = mox.Mox()
        reload(mockconfig)
        self.mockconfig = mockconfig.MockConfig
        self.mockconfig.CERT_REQ = "/tmp/certificates.txt"
        vdt.deploy.certificate.cfg = self.mockconfig

    def tearDown(self):
        self.mox.UnsetStubs()
        if os.path.exists("/tmp/certificates.txt"):
            os.remove("/tmp/certificates.txt")

    def test_is_puppetmaster(self):
        self.mox.StubOutWithMock(vdt.deploy.utils.subprocess,
                                                            'check_output')
        vdt.deploy.utils.subprocess.check_output(['facter', "fqdn"])\
                                            .AndReturn("1234.local.domain")
        vdt.deploy.utils.subprocess.check_output(['facter', "fqdn"])\
                                            .AndReturn("1234.local.domain")
        self.mox.ReplayAll()
        self.assertTrue(vdt.deploy.utils.is_puppetmaster("1234"))
        self.assertFalse(vdt.deploy.utils.is_puppetmaster("1235"))
        self.mox.VerifyAll()

    def test_pending_certificate(self):
        f = open(self.mockconfig.CERT_REQ, "wb")
        f.write("1234\n5678\n")
        f.close()
        # this one is already added, so it should not be added again
        vdt.deploy.certificate.add_pending_certificate("1234")
        f = open(self.mockconfig.CERT_REQ, "r")
        data = f.readlines()
        self.assertEqual(data, ['1234\n', '5678\n'])
        f.close()
        # this one should be added to it
        vdt.deploy.certificate.add_pending_certificate("1111")
        f = open(self.mockconfig.CERT_REQ, "r")
        data = f.readlines()
        self.assertEqual(data, ['1234\n', '5678\n', '1111\n'])
