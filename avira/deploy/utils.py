import collections
import operator
import subprocess
import signal

from straight.plugin import load


__all__ = ('wrap', 'sort_by_key', 'find_by_key', 'find_machine',
           'is_puppetmaster', 'add_pending_certificate',
           'check_call_with_timeout', 'check_output_with_timeout',
           'load_plugin_by_name', 'UnknownPlugin')

PLUGIN_NAMESPACE = 'avira.deployplugin'


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
    """
        Helper method to wrap certain object types
        First wrap dictionary
        >>> result = wrap({'a': 1, 'b': True})
        >>> type(result) == StringCaster
        True

        And now we should have a generator object with wrapped objects
        >>> result = wrap([{'a': 1, 'b': True}])
        >>> type(result.next()) == StringCaster
        True
    """
    if isinstance(obj, collections.MutableMapping):
        return StringCaster(obj)
    elif isinstance(obj, collections.Iterable):
        return (StringCaster(x) for x in obj)


def sort_by_key(sortable, key_name):
    """
        Sort a list of dictionaries by key
        >>> unsorted = [{'name': 'b'}, {'name' : 'a'}]
        >>> sorted(unsorted)
        [{'name': 'a'}, {'name': 'b'}]
    """
    return sorted(sortable, key=operator.itemgetter(key_name))


def find_by_key(iterable, **restrictions):
    """
        Find first occurence of dict in list that matches the key=value restriction

        >>> a = [{"hai": "noob", "lol": "nub"}, {"hai": "nub", "lol": "noob"}]
        >>> find_by_key(a, hai="noob")
        {'hai': 'noob', 'lol': 'nub'}
        >>> find_by_key(a, lol="noob")
        {'hai': 'nub', 'lol': 'noob'}

        We can only have one restriction
        >>> find_by_key(a, lol="noob", somthing="another")
        Traceback (most recent call last):
        ...
        Exception: find_by_key accepts only one restriction
    """

    if len(restrictions) == 1:
        key, value = next(restrictions.iteritems())
        return next((x for x in iterable if str(x[key]) == value), None)
    raise Exception("find_by_key accepts only one restriction")


def find_machine(machine_id, machines):
    """
        Find a machine in a list of dictionaries
        >>> machines = [{'id' : 1111}, {'id': 1112}]
        >>> find_machine('1112', machines)
        {'id': 1112}

        Return nothing if it's not found
        >>> find_machine(1113, machines)
    """
    machine = find_by_key(machines, id=machine_id)
    if machine:
        return wrap(machine)
    return machine


def is_puppetmaster(machine_id):
    # not a failsafe method of checking, but for now
    # no other solution
    fqdn = subprocess.check_output(['facter', "fqdn"])

    if machine_id in fqdn:
        return True
    return False


def check_call_with_timeout(args, timeout_seconds=30, **kwargs):
    process = subprocess.Popen(args, **kwargs)

    old_signal = signal.signal(signal.SIGALRM,
                               lambda _, __: process.terminate())
    signal.alarm(timeout_seconds)

    (stdout, _) = process.communicate()

    # cancel the alarm and reset the signal handler.
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old_signal)
    return stdout


def check_output_with_timeout(args, timeout_seconds=30, **kwargs):
    return check_call_with_timeout(args, timeout_seconds,
                                   stdout=subprocess.PIPE)

class UnknownPlugin(Exception):
    def __init__(self, plugins):
        self.message = "Plugin unknown, try one of %s" % plugins


def load_plugin_by_name(name):
    """
    >>> plugin = load_plugin_by_name('cloudstack')
    >>> plugin.__name__
    'avira.deployplugin.cloudstack'
    >>> plugin.template
    '\\n\\n[cloudstack]\\napiurl = http://mgmt1-dtc1.avira-cloud.net:8080/client/api\\napikey =\\nsecretkey =\\ndomainid = 29\\nzoneid = 6\\ntemplateid = 519\\nserviceid = 17\\ncloudinit_puppet = http://joe.avira-cloud.net/autodeploy/vdt-puppet-agent.cloudinit\\ncloudinit_base = http://joe.avira-cloud.net/autodeploy/vdt-base.cloudinit\\n'
    >>> plugin.Provider.prompt
    'cloudstack> '
    """
    plugins = load(PLUGIN_NAMESPACE)
    full_name = "%s.%s" % (PLUGIN_NAMESPACE, name)
    try:
        plugin = (plugin for plugin in plugins if plugin.__name__ == full_name).next()
        return plugin
    except StopIteration:
        raise UnknownPlugin([plugin.__name__.split('.').pop() for plugin in plugins])
