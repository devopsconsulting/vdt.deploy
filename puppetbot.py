# This signbot must run on the puppetmaster : it will sign the certificates
# for machines which are deployed with the deployment tool.
import time
import os
import syslog
from daemon import runner
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import PUPPET_CERT_DIRECTORY, PUPPET_BINARY, CERT_REQ


class PuppetCertificateHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            try:
                certname = event.src_path.split(os.sep)[-1]
                msg = "Puppet Cert Watchdog: Certificate request for %s" % \
                                                                    certname
                f = open(CERT_REQ)
                ids = [x for x in f.read().split('\n') if not x == '']
                for x in ids:
                    if x in msg:
                        # we found a machine which is deployed by the
                        # deployment tool with a waiting certificate :
                        # sign it
                        msg = "Signing certificate for machine %s" % x
                        ids.remove(x)
                        syslog.syslog(syslog.LOG_ALERT, msg)
                syslog.syslog(syslog.LOG_ALERT, msg)
            except:
                syslog.syslog(syslog.LOG_ALERT, "Error: file %s")


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/null'
        self.stderr_path = '/dev/null'
        self.pidfile_path = '/var/run/signbot.pid'
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
                time.sleep(60)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
