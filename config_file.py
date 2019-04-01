# configuration for Whitesource
def get_version():
    with open('version.txt') as ver_file:
        version_str = ver_file.readline().rstrip()
    return version_str


config_info = {
    'org_token': 'b39d1328-52e2-42e3-98f0-932709daf3f0',
    'check_policies': True,
    'product_name': 'SHC - MLF PYTHON MODEL SERVER OD 1.0',
    'product_version': get_version(),
    'index_url': 'http://nexus.wdf.sap.corp:8081/nexus/content/groups/build.snapshots.pypi/simple/',
    'proxy': {
        'host': 'proxy.wdf.sap.corp',
        'port': '8080',
        'username': '',
        'password': ''
    }
}
