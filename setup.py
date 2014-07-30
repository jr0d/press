from setuptools import setup, find_packages

version = '0.1.3'

setup(name='press',
      version=version,
      description="Automated partitioning, file systems, and image deployment.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jared Rodriguez',
      author_email='jared.rodriguez@rackspace.com',
      url='http://blacknode.net/press',
      license='GPLv2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'pyudev',
          'requests',
          'pyyaml'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
