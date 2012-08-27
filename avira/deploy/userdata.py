#PEP8 --ignore=E501

from StringIO import StringIO
from base64 import encodestring


class UserData(dict):
    """
    Represents a cloud-init user data object

    >>> foo = UserData('http://example.com/', 'test', role='server')
    >>> str(foo)
    'I2luY2x1ZGUgaHR0cDovL2V4YW1wbGUuY29tLwojcHVwcGV0bWFzdGVyPXRlc3QKI3JvbGU9c2Vy\\ndmVyCg==\\n'
    """

    def __init__(self, cloud_init_url, puppetmaster, **kwargs):
        self.cloud_init_url = cloud_init_url
        self['puppetmaster'] = puppetmaster
        self.update(kwargs)

    def base64(self):
        userdata = StringIO()
        userdata.write("#include %s\n" % self.cloud_init_url)
        for data_pair in self.items():
            userdata.write("#%s=%s\n" % data_pair)
        return encodestring(userdata.getvalue())

    __unicode__ = __str__ = base64
