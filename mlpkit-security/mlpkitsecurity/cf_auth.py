import json

from mlpkitsecurity import *
from mlpkitsecurity.token_utils import JWTTokenManager

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))


def _check_tenant_info(request):
    headers = getattr(request, 'headers', None)
    if not headers or 'tenantName' not in headers:
        raise SecurityError('No tenantName header given.')

    use_global_tenant = json.loads(os.environ.get(CLEA_UAA_USE_GLOBAL_TENANT, 'false').lower())
    if use_global_tenant and 'globalTenantName' not in headers:
        raise SecurityError('No globalTenantName header given while being configured to use it.')

    return headers['tenantName'], headers['globalTenantName'] if use_global_tenant else None


def _validate_cf_uaa_config():
    if use_xs_uaa():
        raise SecurityError('Application is expected to configure for CFUAA but configured for XSUAA.', code=500)
    if os.getenv(CLEA_UAA_SERVER_BASE_URL) is None:
        raise SecurityError(CLEA_UAA_SERVER_BASE_URL +
                            ' is not found in environment to work with CFUAA.', code=500)


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
