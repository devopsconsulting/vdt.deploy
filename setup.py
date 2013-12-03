"""
vdt.deploy
============

vdt.deployment provides a command line tool for deploying VM's in Cloudstack
with a puppet role. The puppet role defines the installation and configuration
of the server. For example a server with the role *lvs* will be installed and
configured as an lvs load balancer.
"""

from setuptools import setup
from setuptools import find_packages

version = '1.1.11'

setup(
    name='vdt.deploy',
    version=version,
    description="Vdt Deployment Tool",
    long_description=__doc__,
    classifiers=[],
    # Get strings from
    #http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Martijn Jacobs',
    author_email='martijn@fourdigits.nl',
    url='https://github.com/devopsconsulting/vdt.deploy',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['vdt'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'distribute',
        'watchdog',
        'python-daemon',
        'argh>=0.8.1',
        'pathtools',
        'straight.plugin',
        'argparse',
        'mutexlock',
        # -*- Extra requirements: -*-
    ],
    extras_require={
        'fabric': ['fabric'],
    },
    entry_points={'console_scripts': [
        'vdt-deploy=vdt.deploy.tool:main',
        'vdt-puppetbot=vdt.deploy.puppetbot:main']},
)
