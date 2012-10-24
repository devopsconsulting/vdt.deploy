from config import cfg
import os

def add_pending_certificate(machine_id):
    machine_id = str(machine_id)
    if not os.path.exists(cfg.CERT_REQ):
        f = open(cfg.CERT_REQ, 'w') 
        f.close()
    with open(cfg.CERT_REQ, 'r+') as pending_certificates:
        if machine_id not in pending_certificates.read():
            pending_certificates.write(machine_id)
            pending_certificates.write("\n")
