import logging
import os
import sys
import unittest
from rpy2.rinterface import RRuntimeError

from mlfmodelserver.r_grpc_server import find_model_version as find_model_version
from mlfmodelserver.r_grpc_server import get_model_spec as get_model_spec
from mlfmodelserver.r_grpc_server import load_predict_func as load_predict_func

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))

dirname = os.path.dirname(__file__)
valid_rds_filename = os.path.join(dirname, '../test/resources/r-model/1')
invalid_rds_file = os.path.join(dirname, '../test/resources/r-model/invalid')
valid_base_path = os.path.join(dirname, '../test/resources/r-model')
model_config_file_path = os.path.join(dirname, "resources/r-model/sample_model_config.conf")
invalid_model_config_file_path = os.path.join(dirname, 'resources/r-model/sample_model_config_invalid.conf')

sample_config = {'name': 'fn.rds', 'base_path': '../test/resources/r-model'}


class TestRGrpcServer(unittest.TestCase):

    ''' defining the functions for the unit test case'''
    def test_get_model_spec_valid(self):
        LOG.info("testing get model spec valid")
        print(model_config_file_path)
        self.assertEqual(sample_config, get_model_spec(model_config_file_path, ":"))

    def test_get_model_spec_invalid_config_file_path(self):
        LOG.info("testing get model spec invalid config file path")
        with self.assertRaises(FileNotFoundError) as fnf:
            get_model_spec(invalid_model_config_file_path, ":")
            self.assertEqual("File Not Found", str(fnf))

    def test_get_model_spec_invalid_delimiter(self):
        self.assertNotEqual(sample_config, get_model_spec(model_config_file_path, "#"))

    def test_load_predict_func_valid(self):
        LOG.info("test load predict function valid file")
        unrds_file = load_predict_func(valid_rds_filename)
        self.assertFalse(None, unrds_file)

    def test_load_predict_func_invalid_file_path(self):
        LOG.info("test load predict function invalid file path")
        with self.assertRaises(RRuntimeError) as fnf:
            load_predict_func("../test/resources/r-model/2")
            self.assertEqual('File Not Found', str(fnf))

    def test_load_predict_func_invalid_file(self):
        LOG.info("test load predict function invalid file format , rds format is not used")
        self.assertRaises(Exception, load_predict_func, invalid_model_config_file_path)

    def test_find_model_version_valid(self):
        LOG.info("test find model version valid valid base path")
        self.assertEqual(str(1), find_model_version(valid_base_path))

    def test_find_model_version_invalid_base_path(self):
        LOG.info("test find model version valid invalid base path")
        with self.assertRaises(ValueError) as cm:
            find_model_version(dirname)
            self.assertEqual('No directory named with number in the model base path to denote the version', str(cm))