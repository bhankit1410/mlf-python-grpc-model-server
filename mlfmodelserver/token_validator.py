"""Token Validator"""
import os
import logging
import sys
from mlpkitsecurity.token_utils import JWTTokenManager


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))

_BEGIN_STATEMENT = "-----BEGIN PUBLIC KEY-----"
_END_STATEMENT = "-----END PUBLIC KEY-----"


class TokenValidator:
    """Token Validator"""
    def __init__(self, context, metadata):
        self.context = context
        self.metadata = metadata

    def validate_token(self):
        """Validate token"""
        LOG.info('Start of Validating Token')
        access_token = ""
        for item in self.metadata:
            if item.key == 'authorization':
                access_token = item.value

        if _BEGIN_STATEMENT in os.environ['JWT_VALIDATION_KEY'] and \
                _END_STATEMENT in os.environ['JWT_VALIDATION_KEY']:
            pub_key = os.environ['JWT_VALIDATION_KEY']
            final_public_key = pub_key[len(_BEGIN_STATEMENT):len(pub_key) - len(_END_STATEMENT)]
            formatted_key = _BEGIN_STATEMENT + "\n" + final_public_key + "\n" + _END_STATEMENT
        else:
            formatted_key = _BEGIN_STATEMENT + "\n" + os.environ['JWT_VALIDATION_KEY'] \
                            + "\n" + _END_STATEMENT

        token_manager = JWTTokenManager(None)
        zone_id = token_manager.extract_zone_id(access_token)
        LOG.info('zone id %s', zone_id)
        token_result, tkn = token_manager._offline_validate(access_token, public_key=formatted_key,
                                                            scopes=[os.environ['SCOPES_REQUIRED']])
        return token_result, tkn
