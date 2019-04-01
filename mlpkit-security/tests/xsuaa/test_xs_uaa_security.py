#!/usr/bin/python
import os
import unittest
from tests.xsuaa import setup_env_vars_for_xs_uaa
from mlpkitsecurity.security import _prepare_env_vars, SecurityError
from mlpkitsecurity import MLP_UAA_NEW_TOKEN_CLIENT_ID, MLP_UAA_NEW_TOKEN_CLIENT_SECRET, \
    MLP_MLSERVICE_NAME, MLP_UAA_BASE_URL, VCAP_SERVICES


class TestEnvVarsXsUaa(unittest.TestCase):
    def setUp(self):
        setup_env_vars_for_xs_uaa()

    def tearDown(self):
        setup_env_vars_for_xs_uaa()

    def test_missing_MLP_MLSERVICE_NAME_should_not_cause_error_at_classloading(self):
        del os.environ[MLP_MLSERVICE_NAME]
        _prepare_env_vars() # only logger is called

    def test_missing_VCAP_SERVICES_should_not_cause_error_at_classloading(self):
        del os.environ[VCAP_SERVICES]
        _prepare_env_vars() # only logger is called

    def test_check_xs_uaa_given_valid_VCAP_SERVICES_and_MLP_MLSERVICE_NAME(self):
        os.environ[MLP_MLSERVICE_NAME] = 'test_bs_name'
        os.environ[VCAP_SERVICES] = '''
[
  {
    "xsuaa": [
      {
        "credentials": {
          "uaadomain": "authentication.sap.hana.ondemand.com",
          "clientid": "sb-test_bs_name!t53",
          "clientsecret": "little_secret",
          "url": "https://uaa.com"
        },
        "label": "xsuaa",
        "name": "test_bs_name",
        "plan": "application"
      }
    ]
  }
]
'''
        _prepare_env_vars()
        self.assertEqual(os.environ[MLP_UAA_BASE_URL], "https://uaa.com")
        self.assertEqual(os.environ[MLP_UAA_NEW_TOKEN_CLIENT_ID], "sb-test_bs_name!t53")
        self.assertEqual(os.environ[MLP_UAA_NEW_TOKEN_CLIENT_SECRET], "little_secret")

    def test_xs_uaa_service_name_should_match_MLP_MLSERVICE_NAME(self):
        os.environ[VCAP_SERVICES] = '''
[
  {
    "xsuaa": [
      {
        "credentials": {
          "uaadomain": "authentication.sap.hana.ondemand.com",
          "clientid": "sb-test_bs_name!t53",
          "clientsecret": "little_secret",
          "url": "https://uaa.com"
        },
        "label": "xsuaa",
        "name": "UNMATCHED-MLP_MLSERVICE_NAME",
        "plan": "application"
      }
    ]
  }
]
'''
        self.assertRaises(SecurityError, _prepare_env_vars)

