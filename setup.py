#!/usr/bin/env python

from setuptools import setup, find_packages

with open("basin3d/version.py") as f:
    code = compile(f.read(), "rest_framework/version.py", 'exec')
    exec(code)

with open('docs/quickstart.rst') as readme:
    INSTALL = readme.read()

setup(name='BASIN-3D',
      version=__release__,
      description='Broker for Assimilation, Synthesis and Integration of eNvironmental Diverse, Distributed Datasets',
      long_description=INSTALL,
      author='Val Hendrix',
      author_email='vchendrix@lbl.gov',
      packages=find_packages(exclude=["basin3d.tests", "*.tests.*", "tests.*", "tests"]),
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
