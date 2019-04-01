import os
import unittest
from mlpkitsecurity import VCAP_SERVICES, MLP_FOUNDATION_SERVICE_INSTANCE_NAME, MLP_FOUNDATION_SERVICE_NAME, SecurityError
from rsa import PublicKey
from . import VCAP_SERVICES_V1, VCAP_SERVICES_V2, VCAP_SERVICES_V3
from mlpkitsecurity.vcap_services_util import (
    get_vcap_services,
    get_standard_uaa,
    retrieve_foundation_service_uaa_credentials,
    format_public_key,
    get_xs_app_name,
    get_public_key,
    get_uaa_credentials
)


class TestVcapServicesUtil(unittest.TestCase):

    def setUp(self):
        self._reset_env_vars()

    def tearDown(self):
        self._reset_env_vars()

    @staticmethod
    def _reset_env_vars():
        if os.getenv(VCAP_SERVICES):
            del os.environ[VCAP_SERVICES]
        if os.getenv(MLP_FOUNDATION_SERVICE_NAME):
            del os.environ[MLP_FOUNDATION_SERVICE_NAME]
        if os.getenv(MLP_FOUNDATION_SERVICE_INSTANCE_NAME):
            del os.environ[MLP_FOUNDATION_SERVICE_INSTANCE_NAME]

    def test_get_vcap_services_should_not_throw_error_if_no_VCAP_SERVICES_in_environment(self):
        self.assertIsNone(os.getenv(VCAP_SERVICES))
        self.assertIsNone(get_vcap_services())

    def test_get_vcap_services_with_array_value_should_return_first_item(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V1
        vcap_services = get_vcap_services()
        self.assertIsNotNone(vcap_services)
        self.assertIsNotNone(vcap_services['xsuaa'])

    def test_get_vcap_services_with_single_value(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V3
        vcap_services = get_vcap_services()
        self.assertIsNotNone(vcap_services)
        self.assertIsNotNone(vcap_services['xsuaa'])

    def test_get_standard_uaa(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V3
        vcap_services = get_vcap_services()
        xs_uaa = get_standard_uaa(vcap_services['xsuaa'])
        self.assertEqual('modelrepo_std!b53', xs_uaa['credentials']['xsappname'])

    def test_get_standard_uaa_not_found(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V1
        vcap_services = get_vcap_services()
        with self.assertRaises(SecurityError):
            get_standard_uaa(vcap_services['xsuaa'])

    def test_retrieve_foundation_service_uaa_credentials(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V2
        os.environ[MLP_FOUNDATION_SERVICE_NAME] = 'ml-foundation'
        os.environ[MLP_FOUNDATION_SERVICE_INSTANCE_NAME] = 'ml-foundation-std'
        uaa_credentials = retrieve_foundation_service_uaa_credentials()
        self.assertIsNotNone(uaa_credentials)
        self.assertEqual('https://uaa3.authentication.sap.hana.ondemand.com', uaa_credentials.base_url)

    def test_retrieve_foundation_service_uaa_credentials_invalid_vcap_services(self):
        os.environ[MLP_FOUNDATION_SERVICE_NAME] = 'ml-foundation'
        os.environ[MLP_FOUNDATION_SERVICE_INSTANCE_NAME] = 'service-instance-name'
        os.environ[VCAP_SERVICES] = '''
{
  "ml-foundation": [
   {
    "credentials": {
      "clientid": "sb-808454b9-732b-42d6-a8c5-c3c65404a3ad!b53|modelrepo_std!b53",
      "clientsecret": "modelrepo_std!b53_secret",
      "url": "https://uaa3.authentication.sap.hana.ondemand.com"
    }, "name" : "invalid-service-instance-name"
   }
  ]
}
'''
        with self.assertRaises(SecurityError) as context:
            retrieve_foundation_service_uaa_credentials()
        os.environ[VCAP_SERVICES] = '''
{
  "ml-foundation": [
   {
    "invalid-name": {
      "clientid": "sb-808454b9-732b-42d6-a8c5-c3c65404a3ad!b53|modelrepo_std!b53",
      "clientsecret": "modelrepo_std!b53_secret",
      "url": "https://uaa3.authentication.sap.hana.ondemand.com"
    }, "name" : "service-instance-name"
   }
  ]
}
'''

        self.assertIsNone(retrieve_foundation_service_uaa_credentials())
        os.environ[VCAP_SERVICES] = '''
{
  "ml-foundation": [
   {
    "credentials": {
      "clientid": "sb-808454b9-732b-42d6-a8c5-c3c65404a3ad!b53|modelrepo_std!b53",
      "clientsecret": "modelrepo_std!b53_secret",
      "url": ""
    }, "name" : "service-instance-name"
   }
  ]
}
'''
        self.assertIsNone(retrieve_foundation_service_uaa_credentials())

    def test_format_public_key(self):
        os.environ[VCAP_SERVICES] = VCAP_SERVICES_V3
        vcap_services = get_vcap_services()
        xs_uaa = get_standard_uaa(vcap_services['xsuaa'])
        public_key = xs_uaa['credentials']['verificationkey']
        with self.assertRaises(ValueError):
            PublicKey.load_pkcs1_openssl_pem(public_key)

        formatted_public_key = format_public_key(public_key)
        PublicKey.load_pkcs1_openssl_pem(formatted_public_key)

        reformatted_public_key = format_public_key(formatted_public_key)
        self.assertEqual(formatted_public_key, reformatted_public_key)

    def test_get_xs_app_name(self):
        self.assertIsNone(get_xs_app_name(None))
        self.assertIsNone(get_xs_app_name({'no-xs-app-name': 'some-value'}))
        self.assertEqual('xs-app-name', get_xs_app_name({'xsappname': 'xs-app-name'}))

    def test_get_public_key(self):
        self.assertIsNone(get_public_key(None))
        self.assertIsNone(get_public_key({'no-verificationkey': 'some-value'}))
        self.assertEqual('-----BEGIN PUBLIC KEY-----\nPUBLIC_KEY_HERE\n-----END PUBLIC KEY-----',
                         get_public_key({
                             'verificationkey': '-----BEGIN PUBLIC KEY-----PUBLIC_KEY_HERE-----END PUBLIC KEY-----'})
                         )

    def test_get_uaa_credentials(self):
        os.environ[VCAP_SERVICES] = '{}'
        self.assertIsNone(get_uaa_credentials())

        os.environ[VCAP_SERVICES] = '{"xsuaa": [ {} ]}'
        self.assertIsNone(get_uaa_credentials())

        os.environ[VCAP_SERVICES] = '{"xsuaa": [ {"name": "uaa1"} ]}'
        self.assertIsNone(get_uaa_credentials("non-exist-uaa"))
        self.assertIsNone(get_uaa_credentials())
        self.assertIsNone(get_uaa_credentials("uaa1"))

        os.environ[VCAP_SERVICES] = '{"xsuaa": [ {"name": "uaa1", "credentials":{ "xsappname": "name"}} ]}'
        self.assertIsNone(get_uaa_credentials("non-exist-uaa"))
        self.assertIsNotNone(get_uaa_credentials("uaa1"))
        self.assertIsNotNone(get_uaa_credentials())

