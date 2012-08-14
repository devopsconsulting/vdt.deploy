import collections
import operator
import subprocess
import signal

from avira.deploy.config import CERT_REQ

__all__ = ('wrap', 'sort_by_key', 'find_by_key', 'find_machine',
           'is_puppetmaster', 'add_pending_certificate')


class StringCaster(dict):
    """
    Wraps a dict and adds accessors that cast to string.

    >>> a = StringCaster({'a': 1, 'b': True})
    >>> a.a
    '1'
    >>> a.b
    'True'
    """

    def __init__(self, response):
        self.update(response)

    def __getattr__(self, name):
        attr = self[name]
        if isinstance(attr, collections.Iterable):
            return attr

        return str(attr)


def wrap(obj):
    if isinstance(obj, collections.MutableMapping):
        return StringCaster(obj)
    elif isinstance(obj, collections.Iterable):
        return (StringCaster(x) for x in obj)


def sort_by_key(sortable, key_name):
    return sorted(sortable, key=operator.itemgetter(key_name))


def find_by_key(iterable, **restrictions):
    """
    Find first occurence of dict in list that matches the key=value restriction

    >>> a = [{"hai": "noob", "lol": "nub"}, {"hai": "nub", "lol": "noob"}]
    >>> find_by_key(a, hai="noob")
    {'hai': 'noob', 'lol': 'nub'}
    >>> find_by_key(a, lol="noob")
    {'hai': 'nub', 'lol': 'noob'}
    """

    if len(restrictions) == 1:
        key, value = next(restrictions.iteritems())
        return next((x for x in iterable if str(x[key]) == value), None)
    raise Exception("find_by_key accepts only one restriction")


def find_machine(machine_id, machines):
    machine = find_by_key(machines, id=machine_id)
    if machine:
        return wrap(machine)

    return machine


def is_puppetmaster(machine_id, error):
    # not a failsafe method of checking, but for now
    # no other solution
    fqdn = subprocess.check_output(['facter', "fqdn"])

    if machine_id in fqdn:
        print error
        return

    return False


def add_pending_certificate(machine_id):
    machine_id = str(machine_id)
    with open(CERT_REQ, 'r+') as pending_certificates:
        if machine_id not in pending_certificates.read():
            pending_certificates.write(machine_id)
            pending_certificates.write("\n")


def check_call_with_timeout(args, timeout_seconds=30, **kwargs):
    process = subprocess.Popen(args, **kwargs)

    old_signal = signal.signal(signal.SIGALRM,
                               lambda _, __: process.terminate())
    signal.alarm(timeout_seconds)

    process.wait()

    # cancel the alarm and reset the signal handler.
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old_signal)
