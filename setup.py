#!/usr/bin/env python
import os
import subprocess
import sys

from setuptools import setup, find_packages

# Get the Quickstart documentation
with open('docs/setup.rst') as readme:
    INSTALL = readme.read()

# Update version from latest git tags.
# Create a version file in the root directory
version_py = os.path.join(os.path.dirname(__file__), 'basin3d/version.py')
version_msg = "# Managed by setup.py via git tags.  **** DO NOT EDIT ****"
try:
    git_describe = subprocess.check_output(["git", "describe", "--tags"]).rstrip().decode('utf-8')

    with open(version_py, 'w') as f:
        f.write(version_msg + os.linesep + "__version__ = '" + git_describe.split("-")[0] + "'")
        f.write(os.linesep + "__release__ = '" + git_describe + "'" + os.linesep)

except Exception:
    # If there is an exception, this means that git is not available
    # We will used the existing version.py file
    if not os.path.exists(version_py):
        with open(version_py, 'w') as f:
            f.write(version_msg + os.linesep + "__version__='0'")
            f.write(os.linesep + "__release__='0'" + os.linesep)

__release__ = None
if os.path.exists(version_py):
    with open(version_py) as f:
        code = compile(f.read(), version_py, 'exec')
    exec(code)

if sys.version_info.major == 2:
    sys.exit('Sorry, Python < 2.X is not supported')

if sys.version_info.major == 3 and sys.version_info.minor <= 4:
    sys.exit('Sorry, Python < 3.4 is not supported')

setup(name='BASIN-3D',
      version=__release__,
      description='Broker for Assimilation, Synthesis and Integration of eNvironmental Diverse, Distributed Datasets',
      long_description=INSTALL,
      author='Val Hendrix',
      author_email='vchendrix@lbl.gov',
      packages=find_packages(exclude=["*.tests", ]),
      py_modules=['manage'],
      include_package_data=True,
      install_requires=[
          "django>=2.0,<2.1",
          "djangorestframework",
          "django-filter",
          "django-extensions",
          "python3-keyczar",
          "pyyaml",
          "requests",
          "markdown",
          "pygments"
      ],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django :: 2.0',
          'Framework :: Django :: 2.1',
          'Framework :: Django :: 2.2',
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: GIS',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'opic :: Software Development :: Libraries :: Application Frameworks',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ]
      )
