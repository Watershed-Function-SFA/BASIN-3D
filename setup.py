#!/usr/bin/env python
import os
import sys

import subprocess
from setuptools import setup, find_packages

# Get the Quickstart documentation
with open('docs/quickstart.rst') as readme:
    INSTALL = readme.read()

# Update version from latest git tags.
# Create a version file in the root directory
version_py = os.path.join(os.path.dirname(__file__), 'jaea_geo/version.py')
try:
    git_describe = subprocess.check_output(["git", "describe", "--tags"]).rstrip().decode('utf-8')
    version_msg = "# Managed by setup.py via git tags.  **** DO NOT EDIT ****"
    with open(version_py, 'w') as f:
        f.write(version_msg + os.linesep + "__version__='" + git_describe.split("-")[0] + "'")
        f.write(os.linesep + "__release__='" + git_describe + "'" + os.linesep)

except Exception as e:
    # If there is an exception, this means that git is not available
    # We will used the existing version.py file
    pass

__release__="0"
if os.path.exists(version_py):
      with open(version_py) as f:
          code = compile(f.read(), version_py, 'exec')
      exec(code)

if sys.version_info.major == 2 and sys.version_info.minor < 7:
    sys.exit('Sorry, Python < 2.7 is not supported')

setup(name='BASIN-3D',
      version=__release__,
      description='Broker for Assimilation, Synthesis and Integration of eNvironmental Diverse, Distributed Datasets',
      long_description=INSTALL,
      author='Val Hendrix',
      author_email='vchendrix@lbl.gov',
      packages=find_packages(exclude=["*.tests",]),
      py_modules=['manage'],
      include_package_data=True,
      install_requires=[
          "django >= 1.8, <= 1.9",
          "djangorestframework == 3.4.3",
          "django-filter ==  0.13.0",
          "django-plugins >= 0.3.0",
          "django-extensions >= 1.7.4",
          "python3-keyczar",
          "pyyaml"
      ],
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Web Environment',
          'Framework :: Django :: 1.8',
          'Framework :: Django :: 1.9',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: GIS',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )
