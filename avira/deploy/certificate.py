import os

from avira.deploy.config import cfg
from mutexlock import mutexlock 

def add_pending_certificate(machine_id):
    """
    >>> from avira.deploy.config import cfg
    >>> cfg.CERT_REQ = '/tmp/693c404e9852f2dc8117183bc04db6a0fd975401'
    >>> add_pending_certificate('hai')
    >>> open('/tmp/693c404e9852f2dc8117183bc04db6a0fd975401').read()
    'hai\\n'
    >>> os.remove('/tmp/693c404e9852f2dc8117183bc04db6a0fd975401')
    """
    machine_id = str(machine_id)
    with mutexlock():
        if not os.path.exists(cfg.CERT_REQ):
            f = open(cfg.CERT_REQ, 'w') 
            f.close()
        with open(cfg.CERT_REQ, 'r+') as pending_certificates:
            if machine_id not in pending_certificates.read():
                pending_certificates.write(machine_id)
                pending_certificates.write("\n")

def remove_pending_certificate(machine_id):
    """
    >>> from avira.deploy.config import cfg
    >>> cfg.CERT_REQ = '/tmp/693c404e9852f2dc8117183bc04db6a0fd975401'
    >>> add_pending_certificate('hai')
    >>> open('/tmp/693c404e9852f2dc8117183bc04db6a0fd975401').read()
    'hai\\n'
    >>> add_pending_certificate('koe')
    >>> remove_pending_certificate('hai')
    >>> open('/tmp/693c404e9852f2dc8117183bc04db6a0fd975401').read()
    'koe\\n'
    >>> os.remove('/tmp/693c404e9852f2dc8117183bc04db6a0fd975401')
    """
    machine_id = str(machine_id)
    with mutexlock():
        certs = []
        with open(cfg.CERT_REQ, 'r') as pending_certificates:
            certs = pending_certificates.readlines()
        
        with open(cfg.CERT_REQ, 'w') as empty_file:
            for cert in certs:
                if machine_id not in cert:
                    empty_file.write(cert)
                    # empty_file.write("\n")
