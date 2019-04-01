import os
from mlpkitsecurity import *
import warnings
warnings.simplefilter('ignore', DeprecationWarning)


def setup_env_vars_for_cf_uaa():
    os.environ[CLEA_UAA_SERVER_BASE_URL] = ''
    os.environ[CLEA_UAA_USE_GLOBAL_TENANT] = 'false'
    os.environ.pop(MLP_USE_XSUAA, None)
    os.environ.pop(VCAP_SERVICES, None)
    os.environ.pop(MLP_MLSERVICE_NAME, None)
