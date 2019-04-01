import logging
import cloudpickle
import json
import importlib
import pyspark
import os
import sys
import numpy as np
import pandas as pd
from os import listdir
from os.path import isdir, join
from mlfmodelserver import grpc_server
from pyspark.sql import SparkSession
from numpy import ndarray

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))

IMPORT_ERROR_RETURN_CODE = 3

def load_predict_func(file_path):
    """Load Predict Function"""
    LOG.info("Loading predict function from pkl file {}".format(file_path))
    try:
        with open(file_path, 'rb') as serialized_func_file:
            return cloudpickle.load(serialized_func_file)
    except FileNotFoundError as file_not_found_error:
        raise FileNotFoundError("File Not Found")
    except Exception as generic_exception:
        LOG.error("Exception occured while unpickling {}".format(generic_exception))
        raise generic_exception


def load_pyspark_model(metadata_path, spark, model_path):
    with open(metadata_path, 'r') as metadata:
        metadata = json.load(metadata)
        if "model_class" not in metadata:
            LOG.error("Malformed metadata file.")
            raise Exception
        model_class = metadata["model_class"]
        LOG.info("Loading {} model from {}".format(model_class, model_path))
        splits = model_class.split(".")
        module = ".".join(splits[:-1])
        class_name = splits[-1]
        ModelClass = getattr(importlib.import_module(module), class_name)
        if issubclass(ModelClass, pyspark.ml.pipeline.PipelineModel) or issubclass(ModelClass, pyspark.ml.base.Model):
            model = ModelClass.load(model_path)
        else:
            model = ModelClass.load(spark.sparkContext, model_path)
        return model


def generic_predict_func(predict_func, path):
    """Generic Predict Function"""
    return predict_func(path)

# Refactor to standard json parsing...


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
                     or key.strip().replace("\"", "")):
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
        modules_folder_path = "{dir}/modules/".format(dir=model_base_path)
        sys.path.append(os.path.abspath(modules_folder_path))
        predict_fname = "func.pkl"
        predict_path = "{dir}/{predict_fname}".format(
            dir=model_base_path, predict_fname=predict_fname)
        self.predict_func = load_predict_func(predict_path)

        self.spark = SparkSession.builder.appName("grpc-pyspark").getOrCreate()
        metadata_path = os.path.join(model_base_path, "metadata.json")
        spark_model_path = os.path.join(model_base_path, "pyspark_model_data")
        self.model = load_pyspark_model(metadata_path, self.spark, spark_model_path)

    def wrapper_predict_func(self, inputs):
        """Wrapper for model predict function"""
        print("The deserialized predict func {}".format(dir(self.predict_func)))

        list_inputs = []
        for k in inputs:
            if isinstance(inputs[k], ndarray):
                list_inputs.append(inputs[k].tolist())
            else:
                list_inputs.append(inputs[k])

        preds = self.predict_func(self.spark, self.model, list_inputs)
        return pd.DataFrame({'col': preds})


def start_server():
    """Start server"""
    LOG.info("Starting Pyspark container")

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
    LOG.info("Model config file path from env : %s", model_config_file_path)

    LOG.info("Initializing Pyspark function container")
    sys.stdout.flush()
    sys.stderr.flush()

    try:
        model = ModelContainer(model_config_file_path)
        rpc_service = grpc_server.GrpcServer()
        rpc_service.start(model, port)  # Input to be not specified

    except ImportError as e:
        LOG.error(e)
        sys.exit(IMPORT_ERROR_RETURN_CODE)


if __name__ == "__main__":
    start_server()