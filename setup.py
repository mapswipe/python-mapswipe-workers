from setuptools import setup, find_packages

with open('readme.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='mapswipe-workers',
    version='0.0.2',
    description='Install script for the mapswipe Python workers.',
    author='B. Herfort',
    author_email='',
    url='www.mapswipe.org',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=requirements
)
