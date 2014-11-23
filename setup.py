#!/usr/bin/env python
import codecs
import os
import re
from setuptools import setup, find_packages


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts), encoding='utf8').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='walt',
    description='Tool for turning a series of images into a CSS animation.',
    long_description=read('README.rst'),
    version=find_version('walt.py'),
    packages=find_packages(),
    author='Michael Kelly',
    author_email='me@mkelly.me',
    url='https://github.com/Osmose/walt',
    license='MIT',
    install_requires=[],
    include_package_data=True,
    entry_points={
      'console_scripts':[
          'walt = walt:main'
      ]
   }
)
