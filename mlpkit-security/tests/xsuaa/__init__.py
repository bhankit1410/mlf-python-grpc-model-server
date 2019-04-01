from mlpkitsecurity import *
from mlpkitsecurity.security import _prepare_env_vars

import warnings
warnings.simplefilter('ignore', DeprecationWarning)

test_ml_service_name = 'test_bs_name'
test_vcap_services = '''
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


def setup_env_vars_for_xs_uaa():
    os.environ[MLP_MLSERVICE_NAME] = test_ml_service_name
    os.environ[VCAP_SERVICES] = test_vcap_services
    os.environ[MLP_USE_XSUAA] = 'true'
    _prepare_env_vars()
