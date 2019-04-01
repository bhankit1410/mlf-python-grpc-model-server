import os
import mlpkitsecurity
from mlpkitsecurity import *
from .. import VCAP_SERVICES_V2


def setup_env_vars_for_xs_uaa():
    os.environ[VCAP_SERVICES] = VCAP_SERVICES_V2
    os.environ[MLP_USE_XSUAA] = 'true'
    os.environ[MLP_MLSERVICE_XSAPPNAME] = 'myxsappname!b53'
    os.environ[MLP_MLSERVICE_DEFAULT_SCOPES] = 'read,write'
    os.environ[MLP_UAA_PUBLIC_KEY] = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAx/jN5v1mp/TVn9nTQoYVIUfCsUDHa3Upr5tDZC7mzlTrN2PnwruzyS7w1Jd+StqwW4/vn87ua2YlZzU8Ob0jR4lbOPCKaHIi0kyNtJXQvQ7LZPG8epQLbx0IIP/WLVVVtB8bL5OWuHma3pUnibbmATtbOh5LksQ2zLMngEjUF52JQyzTpjoQkahp0BNe/drlAqO253keiY63FL6belKjJGmSqdnotSXxB2ym+HQ0ShaNvTFLEvi2+ObkyjGWgFpQaoCcGq0KX0y0mPzOvdFsNT+rBFdkHiK+Jl638Sbim1z9fItFbH9hiVwY37R9rLtH1YKi3PuATMjf/DJ7mUluDQIDAQAB\n-----END PUBLIC KEY-----"
    mlpkitsecurity._prepare_env_vars()
