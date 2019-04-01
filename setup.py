from setuptools import setup, find_packages


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


setup(
    name="mlf-python-grpc-model-server",
    version=get_version(),
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'coverage']),
    entry_points={"distutils.commands": ["whitesource_update = plugin.WssPythonPlugin:SetupToolsCommand"]},
    description="Python Model GRPC Server",
    author="Venkat Subramanian",
    author_email="venkat.subramanian@sap.com",
    install_requires=get_install_requires()
)
