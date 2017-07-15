# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ipcwatcher',
    version='0.1.0',
    description='IP Camera Motion Detection',
    long_description=readme,
    author='Bruno Narciso',
    author_email='brunonar@gmail.com',
    url='https://github.com/lucasnar/ipcwatcher',
    license=license,
    packages=find_packages(exclude=('example'))
)
