"""
avira.deploy
============

avira.deployment provides a command line tool for deploying VM's in Cloudstack
with a puppet role. The puppet role defines the installation and configuration
of the server. For example a server with the role *lvs* will be installed and
configured as an lvs load balancer.
"""

from setuptools import setup
from setuptools import find_packages

version = '1.1.4'

setup(
    name='avira.deploy',
    version=version,
    description="Avira Deployment Tool",
    long_description=__doc__,
    classifiers=[],
    # Get strings from
    #http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Martijn Jacobs',
    author_email='martijn@fourdigits.nl',
    url='https://github.dtc.avira.com/VDT/avira.deploy',
    license='Avira VDT 2012',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['avira'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'distribute',
        'watchdog',
        'python-daemon',
        'argh>=0.8.1',
        'pathtools',
        'cloudstack',
        'straight.plugin',
        'argparse',
        # -*- Extra requirements: -*-
    ],
    extras_require={
        'fabric': ['fabric'],
    },
    entry_points={'console_scripts': [
        'avira-deploy=avira.deploy.tool:main',
        'avira-puppetbot=avira.deploy.puppetbot:main']},
)
