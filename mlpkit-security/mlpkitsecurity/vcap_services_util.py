import os
import json
from base64 import b64encode
from mlpkitsecurity.constants import (
    VCAP_SERVICES,
    MLP_XSUAA_SERVICE_NAME,
    MLP_FOUNDATION_SERVICE_NAME,
    MLP_FOUNDATION_SERVICE_INSTANCE_NAME
)
from mlpkitsecurity.exceptions import SecurityError

_begin_statement = "-----BEGIN PUBLIC KEY-----"
_end_statement = "-----END PUBLIC KEY-----"


class UaaBasicCredentials:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def basic_auth_header(self):
        return UaaBasicCredentials.encode(self.client_id, self.client_secret)

    @staticmethod
    def encode(client_id, client_secret):
        basic_auth_credentials = '{}:{}'.format(client_id, client_secret).encode('utf-8')
        basic_auth_credentials = b64encode(basic_auth_credentials).decode('utf-8')
        return 'Basic {}'.format(basic_auth_credentials)

    def __str__(self):
        return '{}:{}'.format(self.base_url, self.basic_auth_header)


def get_vcap_services():
    vcap_raw_value = os.getenv(VCAP_SERVICES)
    if not vcap_raw_value:
        return None

    value = json.loads(vcap_raw_value)
    return value[0] if type(value) in (tuple, list) else value


def get_standard_uaa(xs_uaa_list):
    for xs_uaa in xs_uaa_list:
        if xs_uaa.get('credentials') \
                and xs_uaa['credentials'].get('xsappname') \
                and "_std" in xs_uaa['credentials']['xsappname']:
            return xs_uaa
    raise SecurityError('No std uaa info in vcap services.')


def get_uaa_credentials(uaa_name=None):
    xsuaa_service_name = os.getenv(MLP_XSUAA_SERVICE_NAME, 'xsuaa')
    vcap_services = get_vcap_services()
    if not vcap_services.get(xsuaa_service_name):
        return None

    for xsuaa in vcap_services[xsuaa_service_name]:
        if (not uaa_name or xsuaa.get('name') == uaa_name) and xsuaa.get('credentials'):
            return xsuaa['credentials']

    return None


def get_public_key(uaa_creds):
    if not uaa_creds or not uaa_creds.get('verificationkey'):
        return None

    return format_public_key(uaa_creds['verificationkey'])


def get_xs_app_name(uaa_creds):
    return uaa_creds.get('xsappname') if uaa_creds else None


def retrieve_foundation_service_uaa_credentials():
    service_instance_name = os.getenv(MLP_FOUNDATION_SERVICE_INSTANCE_NAME)
    sb_instance_config = _get_foundation_service_instance_config(service_instance_name)

    if not sb_instance_config \
            or not sb_instance_config.get('credentials'):
        return None

    sb_inst_uaa_credentials = sb_instance_config['credentials']

    if not sb_inst_uaa_credentials['url'] \
            or not sb_inst_uaa_credentials['clientid'] \
            or not sb_inst_uaa_credentials['clientsecret']:
        return None

    return UaaBasicCredentials(base_url=sb_inst_uaa_credentials['url'],
                               client_id=sb_inst_uaa_credentials['clientid'],
                               client_secret=sb_inst_uaa_credentials['clientsecret'])


def _get_foundation_service_instance_config(service_instance_name):
    if not service_instance_name:
        raise SecurityError('MLP_FOUNDATION_SERVICE_INSTANCE_NAME is mandatory.', code=500)

    service_name = os.getenv(MLP_FOUNDATION_SERVICE_NAME, 'ml-foundation')

    vcap_services = get_vcap_services()
    if not vcap_services \
            or not vcap_services.get(service_name):
        raise SecurityError('Unable to find service instance config for MLP_FOUNDATION_SERVICE_NAME=' +
                            str(service_name), code=500)

    if type(vcap_services[service_name]) in (tuple, list):
        for svc_inst_config in vcap_services[service_name]:
            if svc_inst_config.get('name') and svc_inst_config['name'] == service_instance_name:
                return svc_inst_config
    else:
        return vcap_services[service_name]

    raise SecurityError('Unable to find service instance config for MLP_FOUNDATION_SERVICE_INSTANCE_NAME=' +
                        str(service_instance_name), code=500)


def format_public_key(text):
    len_begin_statement = len(_begin_statement)
    if str(text[len_begin_statement: len_begin_statement + 1]) == "\n":
        return text

    len_end_statement = len(_end_statement)
    public_key = _begin_statement + "\n" + str(text[len_begin_statement:-1 * len_end_statement]) + "\n" + _end_statement
    return public_key
