import os
import sys
import logging
import rpy2.robjects as ro
import numpy
from os import listdir
from os.path import isdir, join
from mlfmodelserver import grpc_server
from rpy2.robjects import r, pandas2ri
from numpy import ndarray

IMPORT_ERROR_RETURN_CODE = 3

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))


def load_predict_func(file_path):
    """Load Predict Function"""
    LOG.info("Loading predict function from rds file {}".format(file_path))
    try:
        r.source("../mlfmodelserver/deserialize_model.R")
        return r.get(r.deserialize_model(file_path))
    except Exception as generic_exception:
        LOG.error("Exception occured while unpickling {}".format(generic_exception))
        raise generic_exception


def get_model_spec(config_file_path, delimiter):
    """
    :param config_file_path:
    :param delimiter:
    :return: model spec as key value pair
    """
    model_spec = {}
    try:
        with open(config_file_path) as model_spec_file:
            for line in model_spec_file:
                if delimiter in line:
                    key, value = line.split(delimiter)
                    if key and (key.strip().replace("\"", "").startswith('base_path')
                    or key.strip().replace("\"", "").startswith("name")):
                        model_spec[str(key.strip().replace("\"", ""))] = value.strip().replace("\"", "").replace(",", "")
        return model_spec
    except FileNotFoundError as file_not_found_error:
        raise FileNotFoundError("File Not Found")
    return model_spec


def find_model_version(base_path):
    """Find model version from model folder"""
    # Fetch the version folder from the model base path
    # Validation to see if there is at least one folder named with a digit denoting the version
    # If more than one version folders are present get the max

    try:
        version_dirs = [f for f in listdir(base_path) if (isdir(join(base_path, f))
                                                          and f.isdigit())]
        return max(version_dirs)
    except ValueError as value_error:
        message = "No directory named with number in the model base path to denote the version"
        LOG.error(message)
        raise ValueError(message)


class ModelContainer(grpc_server.ModelContainerBase):
    """Model Container"""
    def __init__(self, model_config_path):
        model_spec = get_model_spec(model_config_path, ':')
        LOG.info("model base path  : %s", model_spec.get('base_path', ''))
        self.model_version = find_model_version(model_spec.get('base_path', ''))
        LOG.info("model version  : %s", self.model_version)
        model_base_path = model_spec['base_path'] + "/" + self.model_version
        LOG.info("model base path with version : %s", model_base_path)
        self.model_name = model_spec.get('name', '')
        LOG.info("model name from config file %s ", self.model_name)
        predict_path = "{dir}".format(dir=model_base_path)
        self.predict_func = load_predict_func(predict_path)

    def wrapper_predict_func(self, inputs):
        """Wrapper for model predict function"""
        """tensor_proto accepts "values" of a python scalar, a python list, a numpy ndarray, or a numpy scalar.
        according to https://www.tensorflow.org/versions/r1.1/api_docs/python/tf/contrib/util/make_tensor_proto"""
        list_inputs = None
        for k in inputs:
            if isinstance(inputs[k], ndarray):
                list_inputs = inputs[k].tolist()
            else:
                list_inputs = inputs[k]

        preds = self.predict_func(list_inputs)
        make_list = ro.r('as.list')
        make_df = ro.r('data.frame')
        rdf_preds = make_df(make_list(preds))
        pdf_preds = pandas2ri.ri2py(rdf_preds)
        return pdf_preds


def start_server():
    """Start server"""
    LOG.info("Starting Python container")

    host_ip = "127.0.0.1"
    if "MODEL_CONTAINER_HOST" in os.environ:
        host_ip = os.environ["MODEL_CONTAINER_HOST"]
    else:
        LOG.info("Connecting to Model Container on localhost")

    port = 9000
    if "MODEL_CONTAINER_PORT" in os.environ:
        port = int(os.environ["MODEL_CONTAINER_PORT"])
    else:
        LOG.info("Connecting to Model Container with default port on port: %s", port)

    model_config_file_path = os.environ["MODELS_CONFIG_FILE_PATH"]
    LOG.info("Model path from env : %s", model_config_file_path)

    LOG.info("Initializing R function container")
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        model = ModelContainer(model_config_file_path)
        rpc_service = grpc_server.GrpcServer()
        rpc_service.start(model, port)
    except ImportError as e:
        LOG.error(e)
        sys.exit(IMPORT_ERROR_RETURN_CODE)


if __name__ == "__main__":
    start_server()
