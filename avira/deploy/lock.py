import errno
import os
import time


class SemaphoreException(Exception):
    """
    An exception that get thrown when an error occurs in the mutex semphore
    context
    """


class mutex(object):
    """
    A semaphore Context Manager that uses a temporary file for locking.
    Only one thread or process can get a lock on the file at once.

    it can be used to mark a block of code as being executed exclusively
    by some thread. see
    `mutex <http://en.wikipedia.org/wiki/Mutual_exclusion>`_.

    usage::

        from __future__ import with_statement
        from avira.deploy.lock import mutex

        with mutex():
            print "hi only one thread will be executing this block of code\
                    at a time."

    Mutex raises an :class:`avira.deploy.lock.SemaphoreException` when it
    has to wait to long to obtain a lock or when it can not determine how long
    it was waiting.

    :param lockfile: The path and name of the pid file used to create the\
         semaphore.
    :param max_wait: The maximum amount of seconds the process should wait to
        obtain the semaphore.
    """

    def __init__(self, lockfile='/tmp/avira.deploy.lock', max_wait=0):
        # the maximum reasonable time for aprocesstobe
        self.max_wait = max_wait

        # the location of the lock file
        self.lockfile = lockfile

    def __enter__(self):
        while True:
            try:
                # if the file exists you can not create it and get an
                # exclusive lock on it. this is an atomic operation.
                file_descriptor = os.open(self.lockfile,
                                          os.O_EXCL | os.O_RDWR | os.O_CREAT)
                # we created the lockfile, so we're the owner
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    # should not occur
                    raise e

            # if we got here the file exists so lets see
            # how long we are waiting for it
            try:
                # the lock file exists, try to stat it to get its age
                # and read it's contents to report the owner PID
                file_contents = open(self.lockfile, "r")
                file_last_modified = os.path.getmtime(self.lockfile)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise SemaphoreException(
                        "%s exists but stat() failed: %s" %
                        (self.lockfile, e.strerror)
                    )
                # we didn't create the lockfile, so it did exist, but it's
                # gone now. Just try again
                continue

            # we didn't create the lockfile and it's still there, check
            # its age
            if self.max_wait != 0 and \
                    time.time() - file_last_modified > self.max_wait:
                pid = file_contents.read()
                raise SemaphoreException(
                    "%s has been locked for more than "
                    "%d seconds by PID %s" % (
                        self.lockfile, self.max_wait, pid
                    )
                )

            # it's not been locked too long, wait a while and retry
            file_contents.close()
            time.sleep(1)

        # if we get here. we have the lockfile. Convert the os.open file
        # descriptor into a Python file object and record our PID in it

        file_handle = os.fdopen(file_descriptor, "w")
        file_handle.write("%d" % os.getpid())
        file_handle.close()

    def __exit__(self, exc_type, exc_value, traceback):
        # Remove the lockfile, releasing the semaphore for other processes
        # to obtain
        os.remove(self.lockfile)
