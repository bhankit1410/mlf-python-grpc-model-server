import logging
import os
import sys

from .constants import *
from .exceptions import *

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))


def b2s(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        return bytes_or_str.decode()
    elif isinstance(bytes_or_str, str):
        return bytes_or_str
    else:
        raise TypeError('Input is neither bytes nor str: %s', bytes_or_str)


def use_xs_uaa():
    return os.getenv(MLP_USE_XSUAA, 'false').lower() == "true"


def get_authorization_header(request):
    headers = getattr(request, 'headers', None)
    if not headers or 'Authorization' not in headers:
        raise SecurityError('No auth header given.')

    return headers['Authorization']


def _prepare_env_vars():
    if use_xs_uaa():
        # either explicitly set the environment variables or bind a UAA master instance to the app
        if (not os.getenv(MLP_UAA_PUBLIC_KEY) and not os.getenv(MLP_UAA_BASE_URL)) or \
                not os.getenv(MLP_MLSERVICE_XSAPPNAME):
            from mlpkitsecurity.vcap_services_util import get_uaa_credentials, get_xs_app_name, get_public_key
            uaa_service_instance_name = os.getenv(MLP_XSUAA_SERVICE_INSTANCE_NAME)
            uaa_creds = get_uaa_credentials(uaa_name=uaa_service_instance_name)
            if uaa_creds:
                LOG.info("Retrieving public key and xsappname from UAA master instance: " +
                         str(uaa_service_instance_name))
                os.environ[MLP_UAA_PUBLIC_KEY] = get_public_key(uaa_creds)
                os.environ[MLP_MLSERVICE_XSAPPNAME] = get_xs_app_name(uaa_creds)
            else:
                LOG.critical('If app is not bound to an XSUAA broker master instance, '
                             'please set MLP_MLSERVICE_XSAPPNAME and either MLP_UAA_BASE_URL or MLP_UAA_PUBLIC_KEY.')

        if not os.getenv(MLP_MLSERVICE_XSAPPNAME):
            LOG.critical('MLP_MLSERVICE_XSAPPNAME is mandatory when configured for XSUAA.')

        if not os.getenv(MLP_FOUNDATION_SERVICE_INSTANCE_NAME):
            LOG.critical('MLP_FOUNDATION_SERVICE_INSTANCE_NAME is mandatory when you need to ' +
                         'retrieve foundation service access token')

        if not os.getenv(MLP_UAA_PUBLIC_KEY) and not os.getenv(MLP_UAA_BASE_URL):
            LOG.critical('Either MLP_UAA_PUBLIC_KEY or MLP_UAA_BASE_URL is mandatory when configured for XSUAA.')
    else:
        if not os.getenv(CLEA_UAA_SERVER_BASE_URL):
            LOG.critical('{CLEA_UAA_SERVER_BASE_URL} is mandatory when configured for CFUAA.'.format(**globals()))
        else:
            LOG.info('Using CFUAA server: %s', os.getenv(CLEA_UAA_SERVER_BASE_URL))


_prepare_env_vars()
