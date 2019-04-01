"""Provides security-related functions for XS UAA flow."""

from mlpkitsecurity import *
from mlpkitsecurity.token_utils import JWTTokenManager

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))


def authorize(original_token=None, request=None, xs_app_name=None, scopes=None):
    """
    To validate OAuth JWT.
    It checks JWT in `Authorization` header of the given `request` object
    against given `xs_app_name` and `scopes`

    This will be offline validation and a public key will be retrieved from configured UAA base URL
    and RSA256 algorithm will be used for validation.

    :param request: request object which should contain a `headers` property
    :param original_token: original token, can be specified explicitly if request object is not provided.
    :param xs_app_name: if not specified, will default to 'xsappname' configured in VCAP_SERVICES
    :param scopes: scopes to validate
    :return: validated `access_token`
    :raises SecurityError: If no authorization token or token is invalid.
    """
    if not use_xs_uaa():
        raise SecurityError('Application is expected to configure for XSUAA but configured for CFUAA.', code=500)

    if not xs_app_name:
        xs_app_name = os.getenv(MLP_MLSERVICE_XSAPPNAME)

    if not scopes:
        default_scopes = os.getenv(MLP_MLSERVICE_DEFAULT_SCOPES)
        if default_scopes:
            scopes = default_scopes.split(",")
        else:
            raise SecurityError('No default auth scopes defined. Parameter `scopes` need to be provided', code=500)

    if not xs_app_name or not scopes:
        raise SecurityError('XS App Name and Scopes are mandatory', code=500)

    try:
        if not original_token:
            original_token = get_authorization_header(request)

        validation_scopes = ['{}.{}'.format(xs_app_name, scope) for scope in scopes]
        token_manager = JWTTokenManager(base_url=os.getenv(MLP_UAA_BASE_URL))
        public_key = os.environ[MLP_UAA_PUBLIC_KEY] = os.getenv(MLP_UAA_PUBLIC_KEY) or token_manager.get_public_key()
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
