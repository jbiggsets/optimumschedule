#!/usr/bin/env python
from setuptools import find_packages, setup


def readme():
    with open('README.rst') as f:
        return f.read()


def requirements():
    req_path = 'requirements.txt'
    with open(req_path) as f:
        reqs = f.read().splitlines()
    return reqs


setup(name='optimumschedule',
      version=0.1,
      description='An optimization module for creating work '
                  'schedules and building rates',
      long_description=readme(),
      keywords=['optimization', 'schedule',]
      maintainer='Jeremy Biggs',
      maintainer_email='jeremy.m.biggs@gmail.com',
      license='Apache 2',
      packages=find_packages(),
      include_package_data=True,
      entry_points={'console_scripts':
                    ['optimize_schedule = optimumschedule.optimize_schedule:main',
                     'optimize_rates = optimumschedule.optimize_rates:main']
                    },
      install_requires=requirements(),
      classifiers=['Intended Audience :: Science/Research',
                   'Intended Audience :: Developers',
                   ],
      zip_safe=False)