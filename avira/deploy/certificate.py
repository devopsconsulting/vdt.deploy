from config import CERT_REQ


def add_pending_certificate(machine_id):
    machine_id = str(machine_id)
    with open(CERT_REQ, 'r+') as pending_certificates:
        if machine_id not in pending_certificates.read():
            pending_certificates.write(machine_id)
            pending_certificates.write("\n")
