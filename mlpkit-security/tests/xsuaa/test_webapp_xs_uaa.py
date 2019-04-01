import os
import unittest
from unittest.mock import Mock, patch

from mlpkitsecurity import (
    MLP_UAA_PUBLIC_KEY,
    b2s,
    MLP_MLSERVICE_NAME,
    MLP_UAA_BASE_URL,
    MLP_USE_XSUAA,
    MLP_UAA_NEW_TOKEN_CLIENT_ID,
    MLP_UAA_NEW_TOKEN_CLIENT_SECRET
)
from mlpkitsecurity.token_utils import TokenCache
from tests.xsuaa import webapp_xs_uaa, setup_env_vars_for_xs_uaa
from tests import bs_token, fs_token


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


class FsAppTestCase(unittest.TestCase):

    def setUp(self):
        setup_env_vars_for_xs_uaa()
        TokenCache()._clear()
        os.environ[MLP_UAA_PUBLIC_KEY] = public_key
        self.app = webapp_xs_uaa.app.test_client()

    def tearDown(self):
        setup_env_vars_for_xs_uaa()
        TokenCache()._clear()
        os.environ.pop(MLP_UAA_PUBLIC_KEY, None)

    def test_raise_SecurityError_if_fs_not_config_for_xsuaa(self):
        del os.environ[MLP_USE_XSUAA]
        data = {'fs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/fs', data=data)
        self.assertEqual(500, resp.status_code)

    def test_authorize_fs_no_auth_header(self):
        os.environ[MLP_MLSERVICE_NAME] = 'test_fs_name'
        data = {'fs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/fs', data=data)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('No auth header given', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_fs_invalid_fs_name(self):
        os.environ[MLP_MLSERVICE_NAME] = 'invalid_test_fs_name'
        headers = {'Authorization': fs_token}
        data = {'fs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/fs', headers=headers, data=data)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('Invalid scope', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_fs_success(self):
        os.environ[MLP_MLSERVICE_NAME] = 'test_fs_name'
        headers = {'Authorization': fs_token}
        data = {'fs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/fs', headers=headers, data=data)
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_raise_SecurityError_if_MLP_MLSERVICE_NAME_not_set(self):
        del os.environ[MLP_MLSERVICE_NAME]
        headers = {'Authorization': fs_token}
        data = {}
        resp = self.app.get('/fs', headers=headers, data=data)
        self.assertIn('MLP_MLSERVICE_NAME is not found in environment to work with XSUAA', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_raise_SecurityError_if_MLP_UAA_BASE_URL_not_set(self):
        del os.environ[MLP_UAA_BASE_URL]
        headers = {'Authorization': fs_token}
        data = {'fs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/fs', headers=headers, data=data)
        self.assertIn('MLP_UAA_BASE_URL is not found in environment to work with XSUAA', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_authorize_fs_success_MLP_UAA_NEW_TOKEN_CLIENT_ID_is_not_mandatory_for_fs(self):
        del os.environ[MLP_UAA_NEW_TOKEN_CLIENT_ID]
        os.environ[MLP_MLSERVICE_NAME] = 'test_fs_name'
        headers = {'Authorization': fs_token}
        data = {'fs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/fs', headers=headers, data=data)
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_authorize_fs_success_MLP_UAA_NEW_TOKEN_CLIENT_SECRET_is_not_mandatory_for_fs(self):
        del os.environ[MLP_UAA_NEW_TOKEN_CLIENT_SECRET]
        os.environ[MLP_MLSERVICE_NAME] = 'test_fs_name'
        headers = {'Authorization': fs_token}
        data = {'fs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/fs', headers=headers, data=data)
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_authorize_fs_success_use_default_fs_name_if_not_specified(self):
        os.environ[MLP_MLSERVICE_NAME] = 'test_fs_name'
        headers = {'Authorization': fs_token}
        data = {}
        resp = self.app.get('/fs', headers=headers, data=data)
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)


class BsAppTestCase(unittest.TestCase):

    def setUp(self):
        setup_env_vars_for_xs_uaa()
        TokenCache()._clear()
        os.environ[MLP_UAA_PUBLIC_KEY] = public_key
        self.app = webapp_xs_uaa.app.test_client()

    def tearDown(self):
        setup_env_vars_for_xs_uaa()
        TokenCache()._clear()
        os.environ.pop(MLP_UAA_PUBLIC_KEY, None)

    def test_raise_SecurityError_if_bs_not_config_for_xsuaa(self):
        del os.environ[MLP_USE_XSUAA]
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train',
                'bs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('Application is expected to configure for XSUAA but configured for CFUAA.', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_authorize_bs_no_auth_header(self):
        os.environ[MLP_MLSERVICE_NAME] = 'test_bs_name'
        data = {'bs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/bs', data=data)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('No auth header given', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_bs_invalid_bs_name(self):
        os.environ[MLP_MLSERVICE_NAME] = 'invalid_test_bs_name'
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train',
                'bs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('Invalid scope', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    @patch('mlpkitsecurity.token_utils.urlopen',
           Mock(return_value=MockResponse('{"access_token":"some_token", "expires_in":100}')))
    def test_authorize_bs_success(self):
        os.environ[MLP_MLSERVICE_NAME] = 'test_bs_name'
        os.environ[MLP_UAA_BASE_URL] = 'https://some-token-retrieval-url.com'
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train',
                'bs_name': os.environ[MLP_MLSERVICE_NAME]}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('Bearer some_token', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    @patch('mlpkitsecurity.token_utils.urlopen',
           Mock(return_value=MockResponse('{"access_token":"some_token", "expires_in":100}')))
    def test_authorize_bs_success_use_default_bs_name_if_not_specified(self):
        os.environ[MLP_MLSERVICE_NAME] = 'test_bs_name'
        os.environ[MLP_UAA_BASE_URL] = 'https://some-token-retrieval-url.com'
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train'}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('Bearer some_token', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_raise_SecurityError_if_MLP_MLSERVICE_NAME_not_set(self):
        del os.environ[MLP_MLSERVICE_NAME]
        os.environ[MLP_UAA_BASE_URL] = 'https://some-token-retrieval-url.com'
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train'}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('MLP_MLSERVICE_NAME is not found in environment to work with XSUAA', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_raise_SecurityError_if_MLP_UAA_BASE_URL_not_set(self):
        del os.environ[MLP_UAA_BASE_URL]
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train'}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('MLP_UAA_BASE_URL is not found in environment to work with XSUAA', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_raise_SecurityError_if_MLP_UAA_NEW_TOKEN_CLIENT_ID_not_set(self):
        del os.environ[MLP_UAA_NEW_TOKEN_CLIENT_ID]
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train'}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('MLP_UAA_NEW_TOKEN_CLIENT_ID is not found in environment to work with XSUAA.', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_raise_SecurityError_if_MLP_UAA_NEW_TOKEN_CLIENT_SECRET_not_set(self):
        del os.environ[MLP_UAA_NEW_TOKEN_CLIENT_SECRET]
        headers = {'Authorization': bs_token}
        data = {'training_name': 'train'}
        resp = self.app.get('/bs', headers=headers, data=data)
        self.assertIn('MLP_UAA_NEW_TOKEN_CLIENT_SECRET is not found in environment to work with XSUAA', b2s(resp.data))
        self.assertEqual(500, resp.status_code)
