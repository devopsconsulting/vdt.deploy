import time
import os
import syslog
from daemon import runner
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import PUPPET_CERT_DIRECTORY


class PuppetCertificateHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            try:
                certname = event.src_path.split(os.sep)[-1]
                msg = "Puppet Cert Watchdog: Certificate request for %s" % \
                                                                    certname
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
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()

app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
