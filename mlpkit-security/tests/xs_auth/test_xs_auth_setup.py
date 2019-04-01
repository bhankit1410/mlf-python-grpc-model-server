#!/usr/bin/python
import os
import unittest
from tests.xs_auth import setup_env_vars_for_xs_uaa
from tests import VCAP_SERVICES_V3
from mlpkitsecurity import (
    _prepare_env_vars,
    VCAP_SERVICES,
    MLP_MLSERVICE_XSAPPNAME,
    MLP_MLSERVICE_DEFAULT_SCOPES,
    MLP_UAA_BASE_URL,
    MLP_UAA_PUBLIC_KEY
)


class TestEnvVarsXsUaa(unittest.TestCase):
    def setUp(self):
        setup_env_vars_for_xs_uaa()

    def tearDown(self):
        setup_env_vars_for_xs_uaa()

    def test_verify_all_necessary_env_vars_are_set(self):
        self.assertIsNotNone(os.getenv(MLP_MLSERVICE_XSAPPNAME))
        self.assertIsNotNone(os.getenv(MLP_MLSERVICE_DEFAULT_SCOPES))
        self.assertIsNotNone(os.getenv(MLP_UAA_PUBLIC_KEY))

    def test_missing_VCAP_SERVICES_should_not_cause_error_at_classloading(self):
        del os.environ[VCAP_SERVICES]
        # only logger is called
        _prepare_env_vars()

    def test_missing_MLP_MLSERVICE_XSAPPNAME_should_not_cause_error_at_classloading(self):
        del os.environ[MLP_MLSERVICE_XSAPPNAME]
        # only logger is called
        _prepare_env_vars()

    def test_missing_MLP_MLSERVICE_DEFAULT_SCOPES_should_not_cause_error_at_classloading(self):
        del os.environ[MLP_MLSERVICE_DEFAULT_SCOPES]
        # only logger is called
        _prepare_env_vars()

    def test_missing_MLP_MLP_UAA_PUBLIC_KEY_should_not_cause_error_at_classloading_if_MLP_UAA_BASE_URL_is_set(self):
        del os.environ[MLP_MLSERVICE_DEFAULT_SCOPES]
        os.environ[MLP_UAA_BASE_URL] = "some-url"
        # no logger called
        _prepare_env_vars()

    def test_missing_MLP_MLP_UAA_PUBLIC_KEY_should_not_cause_error_at_classloading(self):
        del os.environ[MLP_MLSERVICE_DEFAULT_SCOPES]
        # only logger is called
        _prepare_env_vars()

    def test_should_populate_MLP_MLP_UAA_PUBLIC_KEY_and_MLP_MLSERVICE_XSAPPNAME_from_xsuaa_master_instance(self):
        # VCAP_SERVICES contains XSUAA master instance
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V3
        if os.getenv(MLP_UAA_PUBLIC_KEY):
            del os.environ[MLP_UAA_PUBLIC_KEY]
        if os.getenv(MLP_UAA_BASE_URL):
            del os.environ[MLP_UAA_BASE_URL]
        if os.getenv(MLP_MLSERVICE_XSAPPNAME):
            del os.environ[MLP_MLSERVICE_XSAPPNAME]
        _prepare_env_vars()
        self.assertIsNotNone(os.getenv(MLP_UAA_PUBLIC_KEY))
        self.assertIsNotNone(os.getenv(MLP_MLSERVICE_XSAPPNAME))

    def test_should_try_populate_MLP_MLP_UAA_PUBLIC_KEY_and_MLP_MLSERVICE_XSAPPNAME_from_xsuaa_master_instance(self):
        if os.getenv(MLP_UAA_PUBLIC_KEY):
            del os.environ[MLP_UAA_PUBLIC_KEY]
        if os.getenv(MLP_UAA_BASE_URL):
            del os.environ[MLP_UAA_BASE_URL]
        if os.getenv(MLP_MLSERVICE_XSAPPNAME):
            del os.environ[MLP_MLSERVICE_XSAPPNAME]
        _prepare_env_vars()
        # no XS UAA master instance is bound, public key and xsappname couldn't be populated. only logger is called
        self.assertIsNone(os.getenv(MLP_UAA_PUBLIC_KEY))
        self.assertIsNone(os.getenv(MLP_MLSERVICE_XSAPPNAME))
