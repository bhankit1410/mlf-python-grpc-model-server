#!/usr/bin/python
import os
import unittest
from tests.cf_auth import setup_env_vars_for_cf_uaa
from mlpkitsecurity import b2s, CLEA_UAA_SERVER_BASE_URL, _prepare_env_vars


class TestEnvVarsCfUaa(unittest.TestCase):
    def setUp(self):
        setup_env_vars_for_cf_uaa()

    def tearDown(self):
        setup_env_vars_for_cf_uaa()

    def test_check_cf_uaa(self):
        _prepare_env_vars() # only logger is called

    def test_prepare_env_vars_should_not_throw_error_if_CLEA_UAA_SERVER_BASE_URL_is_not_set(self):
        del os.environ[CLEA_UAA_SERVER_BASE_URL]
        _prepare_env_vars() # only logger is called


class TestB2S(unittest.TestCase):
    def test_b2s(self):
        self.assertEqual(b2s('str'), 'str')
        self.assertEqual(b2s(b'bytes'), 'bytes')
        self.assertRaises(TypeError, b2s, [])
