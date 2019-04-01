"""Provides security-related functions."""
import functools
import json
import warnings

from mlpkitsecurity import *
from mlpkitsecurity.token_utils import JWTTokenManager

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))

warnings.simplefilter('default', DeprecationWarning)


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.warn("Call to deprecated function {}.".format(func.__name__), category=DeprecationWarning,
                      stacklevel=2)
        return func(*args, **kwargs)

    return new_func


@deprecated
def _prepare_env_vars():
    if use_xs_uaa():
        if os.getenv(MLP_MLSERVICE_NAME) is None or os.getenv(VCAP_SERVICES) is None:
            LOG.critical('{MLP_MLSERVICE_NAME} and {VCAP_SERVICES} are mandatory when configured for XSUAA.'
                         .format(**globals()))
        else:
            ml_service_name = os.getenv(MLP_MLSERVICE_NAME)
            try:
                xsuaas = json.loads(os.environ[VCAP_SERVICES])[0]['xsuaa']
                assert len(xsuaas) == 1
                xsuaa = xsuaas[0]
                if xsuaa['name'] != ml_service_name:
                    raise ValueError('XSUAA service name in {VCAP_SERVICES} does not match {MLP_MLSERVICE_NAME}'
                                     .format(**globals()))
                os.environ[MLP_UAA_BASE_URL] = xsuaa['credentials']['url']
                os.environ[MLP_UAA_NEW_TOKEN_CLIENT_ID] = xsuaa['credentials']['clientid']
                os.environ[MLP_UAA_NEW_TOKEN_CLIENT_SECRET] = xsuaa['credentials']['clientsecret']
                LOG.info('Using XSUAA server: %s | service name: %s',
                         os.environ[MLP_UAA_BASE_URL], ml_service_name)
            except Exception as err:
                raise SecurityError('Failed to parse ' + VCAP_SERVICES, root_cause=err, code=500)
    else:
        if os.getenv(CLEA_UAA_SERVER_BASE_URL) is None:
            LOG.critical('{CLEA_UAA_SERVER_BASE_URL} is mandatory when configured for CFUAA.'.format(**globals()))
        else:
            LOG.info('Using CFUAA server: %s', os.getenv(CLEA_UAA_SERVER_BASE_URL))


###### deprecated ######
# _prepare_env_vars()  #
###### deprecated ######

@deprecated
def _check_tenant_info(request):
    headers = getattr(request, 'headers', None)
    if not headers or 'tenantName' not in headers:
        raise SecurityError('No tenantName header given.')

    use_global_tenant = json.loads(os.environ.get(CLEA_UAA_USE_GLOBAL_TENANT, 'false').lower())
    if use_global_tenant and 'globalTenantName' not in headers:
        raise SecurityError('No globalTenantName header given while being configured to use it.')

    return headers['tenantName'], headers['globalTenantName'] if use_global_tenant else None


@deprecated
def _validate_cf_uaa_config():
    if use_xs_uaa():
        raise SecurityError('Application is expected to configure for CFUAA but configured for XSUAA.', code=500)
    if os.getenv(CLEA_UAA_SERVER_BASE_URL) is None:
        raise SecurityError(CLEA_UAA_SERVER_BASE_URL +
                            ' is not found in environment to work with CFUAA.', code=500)


@deprecated
def authorize(request, *extra_scopes):
    """
    To validate OAuth JWT.
    It checks JWT in `Authorization` header of the given `request` object
    against given `training_names` (if any) and `tenantName` or `globalTenantName` (configurable).

    This will be offline validation and a public key will be retrieved from configured UAA base URL
    and RSA256 algorithm will be used for validation.

    :param request: request object which should contain a `headers` property
    :param extra_scopes: extra_scopes that should appear in scope list
    :return: `access_token` (with original type prefix, e.g.: `Bearer some_token`).
    :raises SecurityError: If no authorization token or no tenantName/globalTenantName in header or token is invalid.
    """
    _validate_cf_uaa_config()
    try:
        original_token = get_authorization_header(request)
        tenant_name, global_tenant_name = _check_tenant_info(request)
        token_manager = JWTTokenManager(base_url=os.environ[CLEA_UAA_SERVER_BASE_URL])
        public_key = os.environ[MLP_UAA_PUBLIC_KEY] = os.getenv(MLP_UAA_PUBLIC_KEY) or token_manager.get_public_key()
        validation_scopes = [global_tenant_name] if global_tenant_name else [tenant_name]
        validation_scopes.extend(extra_scopes)
        token_ok, access_token = token_manager.validate(access_token=original_token,
                                                        scopes=validation_scopes,
                                                        public_key=public_key,
                                                        online=False)
        assert token_ok
        assert access_token == original_token
        LOG.info("Token is valid. Returning original token...")
        return access_token
    except Exception as err:
        raise SecurityError('Unable to authorize the request.', root_cause=err,
                            code=getattr(err, 'code', 401)) from err


@deprecated
def _validate_xs_uaa_config(is_bs=False):
    if not use_xs_uaa():
        raise SecurityError('Application is expected to configure for XSUAA but configured for CFUAA.', code=500)

    required_vars = [MLP_MLSERVICE_NAME, MLP_UAA_BASE_URL]
    if is_bs:
        required_vars += [MLP_UAA_NEW_TOKEN_CLIENT_ID, MLP_UAA_NEW_TOKEN_CLIENT_SECRET]
    for var in required_vars:
        if os.getenv(var) is None:
            raise SecurityError(var + ' is not found in environment to work with XSUAA.', code=500)


@deprecated
def authorize_fs(original_token=None, request=None, fs_name=None):
    _validate_xs_uaa_config()
    try:
        if not fs_name:
            fs_name = os.environ[MLP_MLSERVICE_NAME]
        assert fs_name

        if not original_token:
            original_token = get_authorization_header(request)

        token_manager = JWTTokenManager(base_url=os.environ[MLP_UAA_BASE_URL])
        public_key = os.environ[MLP_UAA_PUBLIC_KEY] = os.getenv(MLP_UAA_PUBLIC_KEY) or token_manager.get_public_key()
        validation_scopes = [r'^.*\.{}$'.format(fs_name), r'^.*\.sapcustomer$']
        token_ok, access_token = token_manager.validate(access_token=original_token,
                                                        scope_regex=validation_scopes,
                                                        public_key=public_key,
                                                        online=False)
        assert token_ok
        assert access_token == original_token
        LOG.info("Token is valid. Returning original token...")
        return access_token
    except Exception as err:
        raise SecurityError('Unable to authorize the request.', root_cause=err,
                            code=getattr(err, 'code', 401)) from err


@deprecated
def authorize_bs(training_name, original_token=None, request=None, bs_name=None):
    _validate_xs_uaa_config(is_bs=True)
    try:
        if not bs_name:
            bs_name = os.environ[MLP_MLSERVICE_NAME]
        assert bs_name

        if not original_token:
            original_token = get_authorization_header(request)

        token_manager = JWTTokenManager(base_url=os.environ[MLP_UAA_BASE_URL])
        public_key = os.environ[MLP_UAA_PUBLIC_KEY] = os.getenv(MLP_UAA_PUBLIC_KEY) or token_manager.get_public_key()
        tenant_name, suffix = token_manager.extract_tenant_name(original_token)
        validation_scopes = [r'.*\.{}$'.format(bs_name)]
        token_ok, access_token = token_manager.validate(access_token=original_token,
                                                        scope_regex=validation_scopes,
                                                        public_key=public_key,
                                                        online=False)
        assert token_ok
        assert access_token == original_token
        LOG.info("Token is valid. Retrieving new token...")
        retrieval_scopes = ['{}!{}.{}'.format(bs_name, suffix, training_name),
                            '{}!{}.{}'.format(bs_name, suffix, tenant_name)]
        access_token = token_manager.retrieve_token_str((os.environ[MLP_UAA_NEW_TOKEN_CLIENT_ID],
                                                         os.environ[MLP_UAA_NEW_TOKEN_CLIENT_SECRET]),
                                                        scopes=retrieval_scopes)
        assert access_token != original_token, 'Retrieved new token should be different from original token.'
        LOG.info('Returning new token...')
        return access_token
    except Exception as err:
        raise SecurityError('Unable to authorize the request.', root_cause=err,
                            code=getattr(err, 'code', 401)) from err
