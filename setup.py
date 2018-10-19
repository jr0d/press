from setuptools import setup, find_packages

version = '0.5.2'

setup(
    name='press',
    version=version,
    description="An OS image installer that supports customer partitioning, lvm, and software raid",
    long_description='',
    classifiers=[],
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Jared Rodriguez',
    author_email='jared.rodriguez@rackspace.com',
    url='http://github.com/jr0d/press',
    license='GPLv2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyudev',
        'requests',
        'pyyaml',
        'jinja2',
        'ipaddress',
        'six',
        'python-size'
    ],
    entry_points={
        'console_scripts': [
            'press = press.entry:main'
        ]
    }
)
