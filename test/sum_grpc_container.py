from __future__ import print_function
from mlfmodelserver import grpc_server
import sys
import logging
import os

IMPORT_ERROR_RETURN_CODE = 3
INPUT_TYPE_BYTES = 0
INPUT_TYPE_INTS = "int32"
INPUT_TYPE_FLOATS = 2
INPUT_TYPE_DOUBLES = 3
INPUT_TYPE_STRINGS = 4
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

LOG = logging.getLogger(__name__)


class SumContainer(grpc_server.ModelContainerBase):
    def __init__(self, model_spec):
        self.model_name = model_spec.get("model_name")
        self.version = model_spec.get("version")

    def predict_ints(self, inputs):
        sum = 0
        for item in inputs:
            sum += item
        return [sum]

    def predict_floats(self, inputs):
        sum = 0.0
        for item in inputs:
            sum += item
        return [sum]

    def predict_doubles(self, inputs):
        sum = 0.0
        for item in inputs:
            sum += item
        return sum

    def predict_bytes(self, inputs):
        pass

    def predict_strings(self, inputs):
        sum = ""
        for item in inputs:
            sum += item
        return sum

    def get_prediction_function(self, dtype):
        if dtype == INPUT_TYPE_INTS:
            return self.predict_ints
        elif dtype == INPUT_TYPE_FLOATS:
            return self.predict_floats
        elif dtype == INPUT_TYPE_DOUBLES:
            return self.predict_doubles
        elif dtype == INPUT_TYPE_BYTES:
            return self.predict_bytes
        elif dtype == INPUT_TYPE_STRINGS:
            return self.predict_strings
        else:
            print(
                "Attempted to get predict function for invalid model input type!"
            )

    def wrapper_predict_func(self, request):
        preds = {}
        for k, v in request.items():
            predict_func = self.get_prediction_function(v.dtype)
            sum = predict_func(v)
            preds[k] = sum
        return preds


if __name__ == "__main__":

    port = 9000
    model_spec = dict()
    model_spec['model_name'] = "sum-model"
    model_spec['model_version'] = 1
    model_spec['input_type'] = "ints"
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
    os.environ['JWT_VALIDATION_KEY'] = public_key
    os.environ['SCOPES_REQUIRED'] = "mlptestclient"
    os.environ['MODELS_HEALTH_BASE_PATH'] = "/tmp/models"
    os.environ['MODEL_CONTAINER_ID'] = "sum-container_1"
    os.environ['MODEL_CONTAINER_POD_NAME'] = "python-container_1_pod_2"
    os.environ['STATUS_EXPORTER_SLEEP_TIME'] = "60"
    try:
        model = SumContainer(model_spec)
        rpc_service = grpc_server.GrpcServer()
        rpc_service.start(model, port)
    except ImportError as e:
        LOG.error(e)
        sys.exit(IMPORT_ERROR_RETURN_CODE)