# This puppet must run on the puppetmaster : it will sign the certificates
# for machines which are deployed with the deployment tool.
import time
import os
import re
import syslog
import subprocess
from daemon import runner
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import PUPPET_CERT_DIRECTORY, PUPPET_BINARY, CERT_REQ


class PuppetCertificateHandler(FileSystemEventHandler):
    def _certificate_requests(self):
        if os.path.exists(CERT_REQ):
            f = open(CERT_REQ)
            ids = [x for x in f.read().split('\n') if not x == '']
            f.close()
            return ids
        return []

    def _clean_certificate(self, machine_id):
        ids = self._certificate_requests()
        if machine_id in ids:
            ids.remove(machine_id)
        data = "\n".join(ids)
        f = open(CERT_REQ, "w")
        f.write(data)
        f.close()

    def on_created(self, event):
        if not event.is_directory:
            try:
                certname = event.src_path.split(os.sep)[-1]
                certname = os.path.splitext(certname)[0]
                msg = "Puppet Cert Watchdog: Certificate request for %s" % \
                                                                    certname
                syslog.syslog(syslog.LOG_ALERT, msg)
                m = re.search("^i\-[^\-]+\-(\d+)", certname)
                if m:
                    machine_id = m.group(1)
                    ids = self._certificate_requests()
                    if machine_id in ids:
                        msg = "Signing certificate for machine %s" % machine_id
                        syslog.syslog(syslog.LOG_ALERT, msg)
                        res = subprocess.check_output([PUPPET_BINARY,
                                                       "--sign",
                                                       certname])
                        syslog.syslog(syslog.LOG_ALERT, res)
                    else:
                        msg = "Invalid machine %s" % machine_id
                        syslog.syslog(syslog.LOG_ALERT, msg)
                        msg = "Cleaning up certificate %s" % certname
                        syslog.syslog(syslog.LOG_ALERT, msg)
                        res = subprocess.check_output([PUPPET_BINARY,
                                                       "node",
                                                       "clean",
                                                       certname])
                        syslog.syslog(syslog.LOG_ALERT, res)
                # clean up
                self._clean_certificate(machine_id)
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
                          path=PUPPET_CERT_DIRECTORY,
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
