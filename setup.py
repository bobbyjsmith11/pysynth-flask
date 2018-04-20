#! usr/bin/env python
"""
setup for pysynth-flask
"""
from setuptools import setup

def readme():
      """ get the readme file
      """
      with open('README.rst') as f_readme:
            return f_readme.read()

setup(name='pysynth-flask',
      version='0.1',
      description='web gui control for synthesizer',
      long_description=readme(),
      author='Bobby Smith',
      author_email='bobby@epiqsolutions.com',
      packages=['pysynth-flask'],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
