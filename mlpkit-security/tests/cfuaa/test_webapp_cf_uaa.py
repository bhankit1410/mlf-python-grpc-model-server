import os
import unittest

from mlpkitsecurity import (
    MLP_UAA_PUBLIC_KEY,
    b2s,
    CLEA_UAA_USE_GLOBAL_TENANT,
    MLP_USE_XSUAA,
    CLEA_UAA_SERVER_BASE_URL
)
from mlpkitsecurity.token_utils import TokenCache
from tests.cfuaa import webapp_cf_uaa, setup_env_vars_for_cf_uaa
from tests import token_expired_in_2085

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


class AppTestCase(unittest.TestCase):

    def setUp(self):
        setup_env_vars_for_cf_uaa()
        TokenCache()._clear()
        os.environ[MLP_UAA_PUBLIC_KEY] = public_key
        self.app = webapp_cf_uaa.app.test_client()

    def tearDown(self):
        setup_env_vars_for_cf_uaa()
        TokenCache()._clear()
        os.environ.pop(MLP_UAA_PUBLIC_KEY, None)

    def test_authorize_svc_no_auth_header(self):
        headers = {'tenantName': 'mlptestclient'}
        resp = self.app.get('/svc', headers=headers)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('No auth header given', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_svc_no_tenant_name(self):
        headers = {'Authorization': token_expired_in_2085}
        resp = self.app.get('/svc', headers=headers)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('No tenantName header given', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_svc_no_global_tenant_name(self):
        os.environ[CLEA_UAA_USE_GLOBAL_TENANT] = 'true'
        headers = {'tenantName': 'mlptestclient', 'Authorization': token_expired_in_2085}
        resp = self.app.get('/svc', headers=headers)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('No globalTenantName header given', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_svc_success(self):
        headers = {'tenantName': 'mlptestclient', 'Authorization': token_expired_in_2085}
        resp = self.app.get('/svc', headers=headers)
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_raise_SecurityError_if_API_is_configured_to_use_XS_UAA(self):
        os.environ[MLP_USE_XSUAA] = 'true'
        headers = {'tenantName': 'mlptestclient', 'Authorization': token_expired_in_2085}
        resp = self.app.get('/svc', headers=headers)
        self.assertIn('Application is expected to configure for CFUAA but configured for XSUAA', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_raise_SecurityError_if_API_is_CF_UAA_URL_is_not_configured(self):
        del os.environ[CLEA_UAA_SERVER_BASE_URL]
        headers = {'tenantName': 'mlptestclient', 'Authorization': token_expired_in_2085}
        resp = self.app.get('/svc', headers=headers)
        self.assertIn('CLEA_UAA_SERVER_BASE_URL is not found in environment to work with CFUAA', b2s(resp.data))
        self.assertEqual(500, resp.status_code)

    def test_authorize_svc_success_with_global_tenant_name(self):
        os.environ[CLEA_UAA_USE_GLOBAL_TENANT] = 'true'
        headers = {'tenantName': 'mlptestclient', 'globalTenantName': 'mlptestclient', 'Authorization': token_expired_in_2085}
        resp = self.app.get('/svc', headers=headers)
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)
