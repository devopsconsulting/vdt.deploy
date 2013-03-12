# This puppet must run on the puppetmaster : it will sign the certificates
# for machines which are deployed with the deployment tool.
import time
import os
import syslog
import subprocess
from daemon import runner
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from vdt.deploy.config import cfg
from vdt.deploy.certificate import remove_pending_certificate

class PuppetCertificateHandler(FileSystemEventHandler):
    def _certificate_requests(self):
        if os.path.exists(cfg.CERT_REQ):
            f = open(cfg.CERT_REQ)
            ids = [x for x in f.read().split('\n') if not x == '']
            f.close()
            return ids
        return []

    def on_created(self, event):
        if not event.is_directory:
            try:
                certname = event.src_path.split(os.sep)[-1]
                certname = os.path.splitext(certname)[0]
                msg = "Puppet Cert Watchdog: Certificate request for %s" % \
                                                                    certname
                syslog.syslog(syslog.LOG_ALERT, msg)
                machine_id = certname.split(".")[0]
                if machine_id:
                    ids = self._certificate_requests()
                    if machine_id in ids:
                        msg = "Signing certificate for machine %s" % machine_id
                        syslog.syslog(syslog.LOG_ALERT, msg)
                        res = subprocess.check_output([cfg.PUPPET_BINARY,
                                                       "cert",
                                                       "--sign",
                                                       certname])
                        syslog.syslog(syslog.LOG_ALERT, res)
                    else:
                        msg = "Invalid machine %s" % machine_id
                        syslog.syslog(syslog.LOG_ALERT, msg)
                        msg = "Cleaning up certificate %s" % certname
                        syslog.syslog(syslog.LOG_ALERT, msg)
                        res = subprocess.check_output([cfg.PUPPET_BINARY,
                                                       "node",
                                                       "clean",
                                                       certname])
                        syslog.syslog(syslog.LOG_ALERT, res)
                    # clean up
                    remove_pending_certificate(machine_id)
            except Exception, e:
                syslog.syslog(syslog.LOG_ALERT, "Error: %s" % e)


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/var/run/puppetbot.pid'
        self.pidfile_timeout = 5

    def run(self):
        event_handler = PuppetCertificateHandler()
        observer = Observer()
        observer.schedule(event_handler,
                          path=cfg.PUPPET_CERT_DIRECTORY,
                          recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()


def main():
    app = App()
    daemon_runner = runner.DaemonRunner(app)
    daemon_runner.do_action()

if __name__ == '__main__':
    main()
