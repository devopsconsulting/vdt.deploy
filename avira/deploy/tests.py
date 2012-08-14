from unittest import TestCase
from cloudstack.client import Client
from deploy import CloudStackDeployment


class MockCloudStack(object):
    pass


def listVirtualMachines(self, params):
    return [
        {'displayname': 'guiserver',
         'name': 'koe',
         'id': 4045,
         'state': 'Starting'},
        {'displayname': 'rabbitmq',
         'name': 'rabbit',
         'id': 4047,
         'state': 'Running'},
        {'displayname': 'guiserver',
         'name': 'koe',
         'id': 4045,
         'state': 'Fornicating'},
    ]


class DeployToolTest(TestCase):
    def setUp(self):
        self.deploy = CloudStackDeployment()
        self.deploy.client = MockCloudStack()

    def test_do_status(self):
        pass
