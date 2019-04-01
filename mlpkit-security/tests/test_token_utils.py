#!/usr/bin/python
import os
import unittest
from base64 import urlsafe_b64encode

from . import bs_token, token_expired_in_2085, xs_token, VCAP_SERVICES_V2
from unittest.mock import Mock, patch
import time
from mlpkitsecurity.token_utils import (
    TokenCache,
    TokenManager,
    JWTTokenManager,
    TokenError,
    SecurityError,
    validate_scopes,
    retrieve_foundation_service_token,
    extract_zone_id,
    extract_scopes
)
from mlpkitsecurity.vcap_services_util import UaaBasicCredentials
from mlpkitsecurity import VCAP_SERVICES, MLP_FOUNDATION_SERVICE_NAME, MLP_FOUNDATION_SERVICE_INSTANCE_NAME

public_key = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxdRA7iHKUqDkDJM+paEq
luwgUn8MreHZSv/vJ3sdg21GPeXVtROOxLPyn6PBTRGp3UVmWTg+7YnyJrzwatbs
7IT3nti1bN/S/87yLneP/7dGebLreF3IgO2Nq6+foucIfa4wo2wDtjORtY2DgbCo
F7g8uhbjpI/Pt0aem1sU8qH3Tfvmx3C6Sa1uZY/M/lC+XgoQnqcjDTrRl+oYxBPy
h2GDjo1KTGZwCvC1stpbhZYp7dJLvM9bcRI11jpw1wzZ8Q0Uvd8gZ4JCGbYZDGIG
PGMzQ8YvLj509pjb3U8rKFEEfkzI1vK5HXBizgyLHlUEhwh/80w2xUab3+B3rJ1V
BQIDAQAB
-----END PUBLIC KEY-----'''


class MockResponse(object):
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class TestTokenCache(unittest.TestCase):
    def setUp(self):
        self.tc = TokenCache()
        self.tc._clear()

    def tearDown(self):
        self.tc._clear()

    def test_token_cache_is_singleton(self):
        self.assertIs(TokenCache(), self.tc)
        self.assertIs(TokenCache(), TokenCache())

    def test_set_token_ttl_error(self):
        self.assertRaises(TokenError, self.tc.set_token, key='some_key', token='some_token', ttl=-1)

    def test_set_token_success(self):
        self.tc.set_token(key='some_key', token='some_token', ttl=0)
        self.tc.set_token(key='another_key', token='some_token', ttl=1)
        self.assertListEqual(self.tc.__class__._tokens['some_key'], ['some_token', None])
        self.assertEqual(self.tc.__class__._tokens['another_key'][0], 'some_token')
        self.assertIsInstance(self.tc.__class__._tokens['another_key'][1], float)

    def test_get_token_wrong_key(self):
        self.assertRaises(TokenError, self.tc.get_token, key='wrong_key')

    def test_get_token_expired(self):
        key = 'expired_key'
        self.tc.set_token(key=key, token='some_token', ttl=0.01)
        time.sleep(0.02)
        self.assertRaises(TokenError, self.tc.get_token, key=key)
        self.assertNotIn(key, self.tc.__class__._tokens)

    def test_get_token_success(self):
        k1 = 'no_expiry_key'
        k2 = 'valid_key'
        self.tc.set_token(key=k1, token='no_expiry_token', ttl=0)
        self.tc.set_token(key=k2, token='valid_token', ttl=float('inf'))

        self.assertEqual(self.tc.get_token(k1), 'no_expiry_token')
        self.assertEqual(self.tc.get_token(k2), 'valid_token')


class TestTokenManager(unittest.TestCase):

    def test_get_scope_str(self):
        self.assertRaises(SecurityError, TokenManager.get_scope_str, 'string')
        self.assertRaises(SecurityError, TokenManager.get_scope_str, [])
        self.assertEqual(TokenManager.get_scope_str(['scope1', 'scope2']), 'scope1,scope2')

    def test_strip_token_type(self):
        with self.assertRaises(TokenError) as cm:
            TokenManager.strip_token_type('some_token', 'Bearer')
        self.assertIn('Token error', repr(cm.exception))
        self.assertEqual(TokenManager.strip_token_type('Bearer some_token', 'Bearer'), 'some_token')

    def test_b64_compliant_str(self):
        self.assertEqual(TokenManager.b64_compliant_str('some_string'), 'some_string=')
        self.assertEqual(TokenManager.b64_compliant_str('another_string'), 'another_string==')

    def test_b64decode(self):
        original_value = 'some_string'
        encoded_content = urlsafe_b64encode(original_value.encode()).decode()
        self.assertEqual(TokenManager.b64decode(encoded_content).decode(), original_value)

    def test_load_decoded_content_as_json(self):
        original_value = '{ "value": "A" }'
        encoded_content = urlsafe_b64encode(original_value.encode()).decode()
        json = TokenManager.load_decoded_content_as_json(encoded_content)
        self.assertEqual(json['value'], 'A')


class TestJWTTokenManager(unittest.TestCase):
    def setUp(self):
        self.tm = JWTTokenManager('https://www.some_url.com')

    @patch('mlpkitsecurity.token_utils.urlopen',
           Mock(return_value=MockResponse('{{"keys":[{{"value":"{}"}}]}}'.format(public_key.replace('\n', '\\n')))))
    def test_get_public_key(self):
        self.assertEqual(self.tm.get_public_key(), public_key)

    def test_extract_tenant_name(self):
        extracted_tenant, suffix = self.tm.extract_tenant_name(bs_token)
        self.assertEqual((extracted_tenant, suffix), ('some-uuid', 't53'))

    def test_extract_scopes(self):
        extracted_scopes = self.tm.extract_scopes(token_expired_in_2085)
        self.assertListEqual(extracted_scopes, ['mlptestclient'])

    def test_extract_scopes_func(self):
        extracted_scopes = extract_scopes(token_expired_in_2085)
        self.assertListEqual(extracted_scopes, ['mlptestclient'])

    def test_extract_zone_id(self):
        self.assertEqual('uaa', self.tm.extract_zone_id(token_expired_in_2085))
        self.assertEqual('uaa', self.tm.extract_zone_id(xs_token))

    def test_extract_zone_id_func(self):
        self.assertEqual('uaa', extract_zone_id(token_expired_in_2085))
        self.assertEqual('uaa', extract_zone_id(xs_token))

    def test_validate_scopes_ok(self):
        ok, tkn = self.tm.validate_scopes(bs_token, scopes=['some-uuid!t53.test_bs_name'])
        self.assertTrue(ok)
        self.assertEqual(tkn, bs_token)

        ok, tkn = self.tm.validate_scopes(bs_token, scope_regex=[r'^.*\.test_bs_name'])
        self.assertTrue(ok)
        self.assertEqual(tkn, bs_token)

        ok, tkn = self.tm.validate_scopes(token_expired_in_2085, scopes=['mlptestclient'])
        self.assertTrue(ok)
        self.assertEqual(tkn, token_expired_in_2085)

        ok, tkn = self.tm.validate_scopes(token_expired_in_2085, scope_regex=[r'mlptestclient'])
        self.assertTrue(ok)
        self.assertEqual(tkn, token_expired_in_2085)

    def test_validate_scopes_ok_func(self):
        ok, tkn = validate_scopes(bs_token, scopes=['some-uuid!t53.test_bs_name'])
        self.assertTrue(ok)
        self.assertEqual(tkn, bs_token)

        ok, tkn = validate_scopes(bs_token, scope_regex=[r'^.*\.test_bs_name'])
        self.assertTrue(ok)
        self.assertEqual(tkn, bs_token)

        ok, tkn = validate_scopes(token_expired_in_2085, scopes=['mlptestclient'])
        self.assertTrue(ok)
        self.assertEqual(tkn, token_expired_in_2085)

        ok, tkn = validate_scopes(token_expired_in_2085, scope_regex=[r'mlptestclient'])
        self.assertTrue(ok)
        self.assertEqual(tkn, token_expired_in_2085)

    def test_validate_scopes_invalid(self):
        self.assertRaises(SecurityError, self.tm.validate_scopes, bs_token, scopes=['invalid-scope'])
        self.assertRaises(SecurityError, self.tm.validate_scopes,
                          token_expired_in_2085, scopes=['mlptestclient', 'invalid-scope'])
        self.assertRaises(SecurityError, self.tm.validate_scopes,
                          token_expired_in_2085, scope_regex=[r'^.*\.test_bs_name'])

        # opaque token
        self.assertRaises(SecurityError, self.tm.validate_scopes, 'Bearer d1228d2e594e494db2b199c15038be31')

    def test_validate_scopes_invalid_func(self):
        self.assertRaises(SecurityError, validate_scopes, bs_token, scopes=['invalid-scope'])
        self.assertRaises(SecurityError, validate_scopes,
                          token_expired_in_2085, scopes=['mlptestclient', 'invalid-scope'])
        self.assertRaises(SecurityError, validate_scopes,
                          token_expired_in_2085, scope_regex=[r'^.*\.test_bs_name'])

        # opaque token
        self.assertRaises(SecurityError, validate_scopes, 'Bearer d1228d2e594e494db2b199c15038be31')


class TestValidateTokenOnline(unittest.TestCase):
    def setUp(self):
        self.tm = JWTTokenManager('https://www.some_url.com')

    def test_parse_validate_response_not_implemented(self):
        self.assertRaises(NotImplementedError, JWTTokenManager.parse_validate_response, '{{}}')

    def test_validate_online_not_implemented(self):
        self.assertRaises(NotImplementedError, self.tm.validate, '', online=True)


class TestValidateTokenOffline(unittest.TestCase):
    def setUp(self):
        self.tm = JWTTokenManager('https://www.some_url.com')

    def test_validate_token_offline_success(self):
        token_ok, access_token = self.tm.validate(token_expired_in_2085, public_key=public_key)
        self.assertTrue(token_ok)
        self.assertEqual(access_token, token_expired_in_2085)

    def test_validate_token_offline_success_with_scopes(self):
        token_ok, access_token = self.tm.validate(token_expired_in_2085, public_key=public_key, scopes=['mlptestclient'])
        self.assertTrue(token_ok)
        self.assertEqual(access_token, token_expired_in_2085)

    def test_validate_token_offline_success_with_scope_regex(self):
        token_ok, access_token = self.tm.validate(token_expired_in_2085, public_key=public_key, scope_regex=[r'^.*client$'])
        self.assertTrue(token_ok)
        self.assertEqual(access_token, token_expired_in_2085)

    def test_validate_token_offline_invalid_public_key(self):
        token = ''
        self.assertRaises(SecurityError, self.tm.validate, token)

    def test_validate_token_offline_invalid_alg(self):
        token_with_alg_hs256 = 'Bearer eyJhbGciOiAiSFMyNTYiLCAia2lkIjogImxlZ2FjeS10b2tlbi1rZXkiLCAidHlwIjogIkpXVCJ9.eyJqdGkiOiI4Yzk3YWZjM2I4Mzk0N2E5OWVhMjMyNzE3Y2U3ZTFjMyIsInN1YiI6Im1scHRlc3RjbGllbnQiLCJhdXRob3JpdGllcyI6WyJtbHB0ZXN0Y2xpZW50Il0sInNjb3BlIjpbIm1scHRlc3RjbGllbnQiXSwiY2xpZW50X2lkIjoibWxwdGVzdGNsaWVudCIsImNpZCI6Im1scHRlc3RjbGllbnQiLCJhenAiOiJtbHB0ZXN0Y2xpZW50IiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiJiNThjNWQ0ZiIsImlhdCI6MTQ4NjYzNDIzMSwiZXhwIjozNjMxMDgyMjMxLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvdWFhL29hdXRoL3Rva2VuIiwiemlkIjoidWFhIiwiYXVkIjpbIm1scHRlc3RjbGllbnQiXX0.nIl71Dxktizfb5B870Mlh_-62kN9_Wlda8WYbiz3iFaj22LzIUkQiRIAI57g3IwPXbJnJ1tlrf5_DIJpycRxzfxIZnW_GJW56sgY5L4mdPVHSIUHjeFh5v5tGwmOG6a1mYH_H0y8G-nHNolfSejcyvc4RYvcba4kS2nm-wDKKgfqDVaspM4Ktsa15eLHYn1P0LIUEsewTDm3qL_PgbJC3WKq_qgk02B5Or1n0doLkGBtccYlQEZ9lRixmkdov7_4Nl9UNTPgaYchC0AEaxd_RRCBK78FwC6tw3v1X3xJFXoYdJlMNOnTGdbQ4CVP5-Jd7gifPnUilPPPoJmITg0HZQ'
        self.assertRaises(SecurityError, self.tm.validate, token_with_alg_hs256,
                          public_key=public_key)

    def test_validate_token_offline_token_expired(self):
        token_expired = 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiI0YTQwZGFjN2VkMTM0YjJhYTBhZjZiMTg3MmVjOTgzZSIsInN1YiI6Im1scHRlc3RjbGllbnQiLCJhdXRob3JpdGllcyI6WyJtbHB0ZXN0Y2xpZW50Il0sInNjb3BlIjpbIm1scHRlc3RjbGllbnQiXSwiY2xpZW50X2lkIjoibWxwdGVzdGNsaWVudCIsImNpZCI6Im1scHRlc3RjbGllbnQiLCJhenAiOiJtbHB0ZXN0Y2xpZW50IiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiIyNDQ0ZDRiMCIsImlhdCI6MTQ4NjYzNTI0OSwiZXhwIjoxNDg2NjM1MjU5LCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvdWFhL29hdXRoL3Rva2VuIiwiemlkIjoidWFhIiwiYXVkIjpbIm1scHRlc3RjbGllbnQiXX0.DJisxENzMhZVh5ZyWuXpph1ffI3iuDJw4GT1WOfTA5vbxjqVw06LxRhV-061j7LtzyHaOQOjGVUG_QoyHvq-Hx2Ddo-FAYmjXnkUMChLsNNEi-Kb4IjYKs2yRvePRMuIiF673JPUJ0UhS1DS-EC4LZhyCqg41-5eAvOgzFxJIXWbCAAMPmApUVHv10QGqqjDZnTekAKcmJa9-I5XAZksylGyuhsKrN5r-vjsVpoVeGhtJ_ezzCku3PqdQvkYRxOsOZT9aJ5xanYqC7E50uVgG6lAyYIFXO6pfxomU62Iv_1OcqEA27Rvx2w7nEEqhQBYnZitK5c26vCd-UMK-EasQw'
        self.assertRaises(SecurityError, self.tm.validate, token_expired,
                          public_key=public_key)

    def test_validate_token_offline_insufficient_scope(self):
        self.assertRaises(SecurityError, self.tm.validate, token_expired_in_2085, scopes=['some-required-scope', 'mlptestclient'],
                          public_key=public_key)


class TestRetrieveToken(unittest.TestCase):
    def setUp(self):
        self.tm = JWTTokenManager('https://www.some_url.com')
        self.tc = TokenCache()
        self.tc._clear()

    def tearDown(self):
        if os.getenv(VCAP_SERVICES):
            del os.environ[VCAP_SERVICES]
        if os.getenv(MLP_FOUNDATION_SERVICE_NAME):
            del os.environ[MLP_FOUNDATION_SERVICE_NAME]
        if os.getenv(MLP_FOUNDATION_SERVICE_INSTANCE_NAME):
            del os.environ[MLP_FOUNDATION_SERVICE_INSTANCE_NAME]

    @patch('mlpkitsecurity.token_utils.urlopen',
           Mock(return_value=MockResponse('{"access_token":"some_token", "expires_in":100}')))
    def test_retrieve_token_str_with_cache(self):
        # cred is plain text
        cred = ['client', 'secret']
        token_str = self.tm.retrieve_token_str(token_retrieval_cred=cred,
                                               scopes=['scope'],
                                               use_cache=True)
        self.assertEqual(token_str, 'Bearer some_token')
        cache_key = 'mlp::{}scope'.format(str(cred))
        self.assertEqual(self.tc.__class__._tokens[cache_key][0], 'some_token')
        self.assertIsInstance(self.tc.__class__._tokens[cache_key][1], float)

        # cred is UaaBasicCredenticals
        cred = UaaBasicCredentials(self.tm.base_url, 'client', 'secret')
        token_str = self.tm.retrieve_token_str(token_retrieval_cred=cred,
                                               scopes=['scope'],
                                               use_cache=True)
        self.assertEqual(token_str, 'Bearer some_token')
        cache_key = 'mlp::{}scope'.format(str(cred))
        self.assertEqual(self.tc.__class__._tokens[cache_key][0], 'some_token')
        self.assertIsInstance(self.tc.__class__._tokens[cache_key][1], float)

    @patch('mlpkitsecurity.token_utils.urlopen',
           Mock(return_value=MockResponse('{"access_token":"some_token", "expires_in":100}')))
    def test_retrieve_token_str_without_cache(self):
        token_str = self.tm.retrieve_token_str(token_retrieval_cred=['client', 'secret'],
                                               scopes=['scope'],
                                               use_cache=False)
        self.assertEqual(token_str, 'Bearer some_token')

    @patch('mlpkitsecurity.token_utils.urlopen',
           Mock(return_value=MockResponse('{"access_token":"some_token", "expires_in":100}')))
    def test_parse_retrieve_response(self):
        res = self.tm.retrieve(token_retrieval_cred=['client', 'secret'])
        self.assertEqual(self.tm.parse_retrieve_response(res), 'some_token')

    @patch('mlpkitsecurity.token_utils.urlopen',
           Mock(return_value=MockResponse('{"access_token":"some_token", "expires_in":100}')))
    def test_retrieve_token_for_a_given_service_broker_instance_name(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V2
        os.environ[MLP_FOUNDATION_SERVICE_NAME] = 'ml-foundation'
        os.environ[MLP_FOUNDATION_SERVICE_INSTANCE_NAME] = 'ml-foundation-std'
        token_str = retrieve_foundation_service_token()
        self.assertEqual(token_str, 'Bearer some_token')

    def test_retrieve_token_for_an_invalid_foundation_service_instance_name(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V2
        os.environ[MLP_FOUNDATION_SERVICE_NAME] = 'ml-foundation'
        os.environ[MLP_FOUNDATION_SERVICE_INSTANCE_NAME] = 'invalid-name'
        with self.assertRaises(SecurityError) as context:
            retrieve_foundation_service_token()
        self.assertEqual(context.exception.code, 500)
        self.assertEqual(context.exception.detail_info,
                         'Unable to find service instance config for MLP_FOUNDATION_SERVICE_INSTANCE_NAME=invalid-name')

    def test_retrieve_token_expect_foundation_service_instance_name(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V2
        os.environ[MLP_FOUNDATION_SERVICE_NAME] = 'ml-foundation'
        with self.assertRaises(SecurityError) as context:
            retrieve_foundation_service_token()
        self.assertEqual(context.exception.code, 500)
        self.assertEqual(context.exception.detail_info, 'MLP_FOUNDATION_SERVICE_INSTANCE_NAME is mandatory.')

    def test_retrieve_token_expect_foundation_service_name(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V2
        os.environ[MLP_FOUNDATION_SERVICE_NAME] = 'invalid-foundation-service-name'
        os.environ[MLP_FOUNDATION_SERVICE_INSTANCE_NAME] = 'ml-foundation-std'
        with self.assertRaises(SecurityError) as context:
            retrieve_foundation_service_token()
        self.assertEqual(context.exception.code, 500)
        self.assertEqual(context.exception.detail_info,
                         'Unable to find service instance config for '
                         'MLP_FOUNDATION_SERVICE_NAME=invalid-foundation-service-name')
