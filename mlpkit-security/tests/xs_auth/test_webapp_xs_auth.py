import os
import unittest

from mlpkitsecurity import (
    MLP_UAA_PUBLIC_KEY,
    b2s,
    MLP_USE_XSUAA
)
from mlpkitsecurity.token_utils import TokenCache
from mlpkitsecurity.vcap_services_util import format_public_key
from tests.xs_auth import webapp_xs_auth, setup_env_vars_for_xs_uaa
from tests import xs_token


public_key = "-----BEGIN PUBLIC KEY-----MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxdRA7iHKUqDkDJM+paEqluwgUn8MreHZSv/vJ3sdg21GPeXVtROOxLPyn6PBTRGp3UVmWTg+7YnyJrzwatbs7IT3nti1bN/S/87yLneP/7dGebLreF3IgO2Nq6+foucIfa4wo2wDtjORtY2DgbCoF7g8uhbjpI/Pt0aem1sU8qH3Tfvmx3C6Sa1uZY/M/lC+XgoQnqcjDTrRl+oYxBPyh2GDjo1KTGZwCvC1stpbhZYp7dJLvM9bcRI11jpw1wzZ8Q0Uvd8gZ4JCGbYZDGIGPGMzQ8YvLj509pjb3U8rKFEEfkzI1vK5HXBizgyLHlUEhwh/80w2xUab3+B3rJ1VBQIDAQAB-----END PUBLIC KEY-----"


class MockResponse(object):
    def __init__(self, content):
        self.content = content

    def read(self):
        return self.content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class XsAuthAppTestCase(unittest.TestCase):

    _valid_data = {'scopes': 'read,write', 'xs_app_name': 'myxsappname!b53'}

    def setUp(self):
        setup_env_vars_for_xs_uaa()
        TokenCache()._clear()
        os.environ[MLP_UAA_PUBLIC_KEY] = format_public_key(public_key)
        self.app = webapp_xs_auth.app.test_client()

    def tearDown(self):
        setup_env_vars_for_xs_uaa()
        TokenCache()._clear()
        os.environ.pop(MLP_UAA_PUBLIC_KEY, None)

    def test_raise_SecurityError_if_service_not_config_for_xsuaa(self):
        del os.environ[MLP_USE_XSUAA]
        resp = self.app.get('/authorize', data=self._valid_data)
        self.assertEqual(500, resp.status_code)

    def test_authorize_no_auth_header(self):
        resp = self.app.get('/authorize', data=self._valid_data)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('No auth header given', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_invalid_xs_app_name(self):
        headers = {'Authorization': xs_token}
        data = {'scopes': 'read,write', 'xs_app_name': 'invalid-xs-app-name'}
        resp = self.app.get('/authorize', headers=headers, data=data)
        self.assertIn('Unable to authorize the request', b2s(resp.data))
        self.assertIn('Invalid scope', b2s(resp.data))
        self.assertEqual(401, resp.status_code)

    def test_authorize_success(self):
        headers = {'Authorization': xs_token}
        resp = self.app.get('/authorize', headers=headers, data=self._valid_data)
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_authorize_success_with_default_xsappname(self):
        headers = {'Authorization': xs_token}
        resp = self.app.get('/authorize', headers=headers, data={'scopes': 'read,write'})
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_authorize_success_with_default_scopes(self):
        headers = {'Authorization': xs_token}
        # no scopes passed in. use default scopes defined in the ML services
        resp = self.app.get('/authorize', headers=headers, data={'xs_app_name': 'myxsappname!b53'})
        self.assertIn('authorized!', b2s(resp.data))
        self.assertEqual(200, resp.status_code)

    def test_raise_SecurityError_if_scopes_are_invalid(self):
        headers = {'Authorization': xs_token}
        data = {'scopes': 'invalid', 'xs_app_name': 'myxsappname!b53'}
        resp = self.app.get('/authorize', headers=headers, data=data)
        self.assertIn("Unable to authorize the request.\nError code 401: Invalid scope: ['myxsappname!b53.invalid']",
                      b2s(resp.data))
        self.assertEqual(401, resp.status_code)
