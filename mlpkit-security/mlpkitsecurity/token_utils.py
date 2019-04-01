import json
import time
import re
import abc
from base64 import urlsafe_b64decode
from urllib.request import urlopen, Request
from urllib.parse import urljoin, urlencode
from rsa import PublicKey
import rsa
from mlpkitsecurity import (
    SecurityError,
    TokenError,
    b2s,
)
from mlpkitsecurity.vcap_services_util import retrieve_foundation_service_uaa_credentials, UaaBasicCredentials


def retrieve_foundation_service_token():
    """
    To retrieve new token from uaa credentials configured for foundation service instance.

    :return: new `access_token` retrieved from given UAA credentials
    :raises SecurityError: If unable to retrieve new token
    """
    uaa_creds = retrieve_foundation_service_uaa_credentials()
    if not uaa_creds:
        raise SecurityError('UAA credentials for foundation service is missing', code=500)

    try:
        token_manager = JWTTokenManager(base_url=uaa_creds.base_url)
        access_token = token_manager.retrieve_token_str(uaa_creds, use_cache=False)
        return access_token
    except Exception as err:
        raise SecurityError('Unable to retrieve new token.' + str(err), root_cause=err,
                            code=getattr(err, 'code', 401)) from err


def validate_scopes(access_token, scopes=None, scope_regex=None):
    """
    Only scopes in the access_token's payload will be checked.

    Validity of the access_token in other aspects will NOT be verified.

    :raise SecurityError: invalid scopes in access_token
    :param access_token: original JWT
    :param scopes: if present and not None, will be used for validation
    :param scope_regex: only be checked against when scopes is not present or None
    :return: (True, access_token) if valid scope(s)
    """

    return JWTTokenManager(base_url=None).validate_scopes(access_token, scopes=scopes, scope_regex=scope_regex)


def extract_scopes(access_token):
    """Extract scope list from jwt as list of strs."""

    return JWTTokenManager(base_url=None).extract_scopes(access_token)


def extract_zone_id(access_token):
    """Extract zone id from jwt."""

    return JWTTokenManager(base_url=None).extract_zone_id(access_token)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TokenCache(object, metaclass=Singleton):
    _tokens = {}

    def set_token(self, key, token, *, ttl=3600):
        if ttl < 0:
            raise TokenError('Time-to-live must be non-negative integer')

        self.__class__._tokens[key] = [token, None if ttl == 0 else (time.time() + ttl)]

    def get_token(self, key):

        if key not in self.__class__._tokens:
            raise TokenError('Token key not in cache.')

        token, expiry_time = self.__class__._tokens[key]

        if isinstance(expiry_time, float) and expiry_time <= time.time():
            del self.__class__._tokens[key]
            raise TokenError('Token in cache expired.')

        return token

    def _clear(self):
        self.__class__._tokens.clear()


class TokenManager(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def token_type(self):
        """Token type"""

    @abc.abstractmethod
    def validate(self, access_token, *, scopes=None, public_key=None, online=False):
        """Validate token"""

    @staticmethod
    @abc.abstractstaticmethod
    def parse_validate_response(validate_resp):
        """Parse token validation response

        :param validate_resp:
        :return: Parsed response.
        """

    @abc.abstractmethod
    def retrieve(self, token_retrieval_cred, *, scopes=None):
        """Retrieve token"""

    @staticmethod
    @abc.abstractstaticmethod
    def parse_retrieve_response(retrieve_resp):
        """Parse token retrieval response

        :param retrieve_resp:
        :return: parsed response.
        """

    @staticmethod
    def get_scope_str(scopes):
        if not scopes or not isinstance(scopes, list):
            raise SecurityError('Invalid auth scope(s): {}'.format(scopes))

        return ','.join(map(str, scopes))

    @staticmethod
    def strip_token_type(access_token, token_type):
        """
        Strip off token type from access token.

        :raise AssertionError: access_token doesn't start with token_type
        :param access_token: token with token type.
        :param token_type: case-sensitive token type; leading and trailing spaces will be striped off. e.g.: 'Bearer'
        :return: type-striped access token. Original token will not be mutated.
        """
        # TODO: The token type check can be improved by using regex
        if not access_token.startswith(token_type.strip() + ' '):
            raise TokenError('Access token was not prefixed with token type: {}'.format(token_type))

        return access_token[len(token_type) + 1:]

    @staticmethod
    def b64_compliant_str(astr):
        """pad string to be base64 compliant"""
        return astr + '=' * (-len(astr) % 4)

    @staticmethod
    def b64decode(encoded_content):
        return urlsafe_b64decode(TokenManager.b64_compliant_str(encoded_content))

    @staticmethod
    def load_decoded_content_as_json(encoded_content):
        return json.loads(b2s(TokenManager.b64decode(encoded_content)))


class JWTTokenManager(TokenManager):
    def __init__(self, base_url):
        self.base_url = base_url

    @property
    def token_type(self):
        return 'Bearer'

    def retrieve_token_str(self, token_retrieval_cred, *, scopes=None, use_cache=False):
        if use_cache:
            tkn_key = 'mlp::' + str(token_retrieval_cred)
            if scopes:
                tkn_key += TokenManager.get_scope_str(scopes)
            try:
                tkn = TokenCache().get_token(tkn_key)
            except TokenError:
                resp = self.retrieve(token_retrieval_cred, scopes=scopes)
                ttl = max(1, json.loads(b2s(resp))['expires_in'] - 5)
                tkn = JWTTokenManager.parse_retrieve_response(resp)
                TokenCache().set_token(tkn_key, token=tkn, ttl=ttl)
        else:
            resp = self.retrieve(token_retrieval_cred, scopes=scopes)
            tkn = JWTTokenManager.parse_retrieve_response(resp)
        return '{} {}'.format(self.token_type, tkn)

    @staticmethod
    def parse_retrieve_response(retrieve_resp):
        return json.loads(b2s(retrieve_resp))['access_token']

    def retrieve(self, token_retrieval_cred, *, scopes=None):
        """Retrieve token from UAA server.

        :param token_retrieval_cred: is either a UaaBasicCredentials or (client_id, client_secret)
        :param scopes: optional scopes
        :return: raw token retrieval response
        """
        payload = {'grant_type': 'client_credentials'}
        try:
            payload['scope'] = TokenManager.get_scope_str(scopes)
        except SecurityError:
            pass
        data = urlencode(payload).encode('utf-8')
        req = Request(url=urljoin(self.base_url, 'oauth/token'), data=data)
        req.add_header('cache-control', 'no-cache')
        req.add_header('content-type', 'application/x-www-form-urlencoded')
        req.add_header('authorization', (token_retrieval_cred.basic_auth_header
                                         if hasattr(token_retrieval_cred, 'basic_auth_header')
                                         else UaaBasicCredentials.encode(*token_retrieval_cred)))

        with urlopen(req) as f:
            return f.read()

    @staticmethod
    def parse_validate_response(validate_resp):
        raise NotImplementedError('Online validation is not supported.')

    def validate(self, access_token, *, scopes=None, scope_regex=None, public_key=None, online=False):
        if online:
            return JWTTokenManager.parse_validate_response(
                self._online_validate(access_token, scopes=scopes)), access_token
        else:
            if not public_key:
                raise SecurityError('Invalid public key: {}'.format(public_key))
            return self._offline_validate(access_token, public_key, scopes=scopes, scope_regex=scope_regex)

    def _online_validate(self, access_token, scopes=None):
        raise NotImplementedError('Online validation is not supported.')

    def _offline_validate(self, access_token, public_key, scopes=None, scope_regex=None):
        verified, payload = self._validate_token_against_public_key(access_token, public_key)
        assert verified
        json_payload = TokenManager.load_decoded_content_as_json(payload)
        JWTTokenManager._validate_payload_expiry(json_payload)
        JWTTokenManager._validate_scopes_in_payload(json_payload, scopes=scopes, scope_regex=scope_regex)
        return True, access_token

    def _validate_token_against_public_key(self, access_token, public_key):
        header, encoded_payload, signature = self._split_header_payload_signature_from_token(access_token)
        headers = TokenManager.load_decoded_content_as_json(header)
        if headers['alg'] != 'RS256':
            # As public key is used, algorithm has to be RS256
            raise SecurityError('Invalid algorithm!', code=401)

        decoded_signature = TokenManager.b64decode(signature)
        pubkey = PublicKey.load_pkcs1_openssl_pem(public_key)
        message = header + '.' + encoded_payload
        verified = rsa.verify(message.encode('utf-8'), decoded_signature, pubkey)
        return verified, encoded_payload

    @staticmethod
    def _validate_payload_expiry(json_payload):
        if float(json_payload['exp']) <= time.time():
            raise SecurityError('Token expired!', code=401)

    @staticmethod
    def _validate_scopes_in_payload(json_payload, scopes=None, scope_regex=None):
        JWTTokenManager._validate_scopes(json_payload['scope'], scopes=scopes, scope_regex=scope_regex)

    @staticmethod
    def _validate_scopes(scope_list, scopes=None, scope_regex=None):
        if scopes:
            scopes_in_token = set(scope_list)
            if any(expected_scope not in scopes_in_token for expected_scope in scopes):
                raise SecurityError('Invalid scope: {}'.format(scopes), code=401)
        elif scope_regex:
            scopes_in_token = scope_list
            assert len(scope_regex) == len(scopes_in_token), \
                'Number of scopes in token should match number of validation scope_regex.'
            assert isinstance(scope_regex, list) and len(scope_regex) in (1, 2)
            for scope_in_token in scopes_in_token:
                if bool(re.match(scope_regex[-1], scope_in_token)):
                    scope_regex.pop()
                elif bool(re.match(scope_regex[0], scope_in_token)):
                    scope_regex.pop(0)
                else:
                    raise SecurityError('Invalid scope regex: {}'.format(scope_regex), code=401)

    def _split_header_payload_signature_from_token(self, access_token):
        tkn = TokenManager.strip_token_type(access_token, token_type=self.token_type)
        split_payload = tkn.split('.')
        if len(split_payload) != 3:
            raise TokenError('Unexpected token payload: token cannot be opaque.')
        else:
            return split_payload

    def extract_scopes(self, access_token):
        json_payload = self._extract_json_payload(access_token)
        return json_payload['scope']

    def extract_zone_id(self, access_token):
        json_payload = self._extract_json_payload(access_token)
        return json_payload['zid']

    def _extract_json_payload(self, access_token):
        _, encoded_payload, _ = self._split_header_payload_signature_from_token(access_token)
        return TokenManager.load_decoded_content_as_json(encoded_payload)

    def extract_tenant_name(self, access_token):
        """
        Experimental API.

        Only for XSUAA auth flow.
        """

        temp = self.extract_scopes(access_token)[0]
        matched = re.match(r'^.*!.*\.', temp).group(0)
        i = matched.index('!')
        tenant_name = matched[:i]
        suffix = matched[i + 1:-1]
        return tenant_name, suffix

    def get_public_key(self):
        """Retrieve public key from UAA base url."""

        req = Request(urljoin(self.base_url, 'token_keys'))
        with urlopen(req) as f:
            return json.loads(b2s(f.read()))['keys'][0]['value']

    def validate_scopes(self, access_token, scopes=None, scope_regex=None):
        try:
            _, encoded_payload, _ = self._split_header_payload_signature_from_token(access_token)
            json_payload = TokenManager.load_decoded_content_as_json(encoded_payload)
            JWTTokenManager._validate_scopes_in_payload(json_payload, scopes=scopes, scope_regex=scope_regex)
            return True, access_token
        except Exception as err:
            raise SecurityError('Unable to validate scopes.', root_cause=err,
                                code=getattr(err, 'code', 401)) from err
