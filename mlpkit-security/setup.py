"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open


def get_version():
    with open('version.txt') as ver_file:
        version_str = ver_file.readline().rstrip()
    return version_str


def get_install_requires():
    reqs = []
    with open('requirements.txt') as reqs_file:
        for line in iter(lambda: reqs_file.readline().rstrip(), ''):
            reqs.append(line)
    return reqs


def get_extras_require():
    with open('test-requirements.txt') as reqs_file:
        reqs = [line.rstrip() for line in reqs_file.readlines()]
    return {'test': reqs}


setup(name="sapclea-mlpkit-security",
      version=get_version(),
      entry_points={"distutils.commands": ["whitesource_update = plugin.WssPythonPlugin:SetupToolsCommand"]},
      packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'coverage', 'scripts']),
      description="SAP Leonardo ML Foundation mlpkit-security",
      install_requires=get_install_requires(),
      extras_require=get_extras_require()
      )
