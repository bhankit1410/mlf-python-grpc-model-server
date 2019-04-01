import logging
import sys
import os
import unittest
import sys
import pickle


absFilePath = os.path.abspath(__file__)
fileDir = os.path.dirname(os.path.abspath(__file__))
parentDir = os.path.dirname(fileDir)
parentDir = parentDir+'/src'
sys.path.append(parentDir)

from mlfmodelserver.python_grpc_server import find_model_version as find_model_version
from mlfmodelserver.python_grpc_server import get_model_spec as get_model_spec
from mlfmodelserver.python_grpc_server import load_predict_func as load_predict_func



LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))

dirname = os.path.dirname(__file__)
valid_pkl_filename = os.path.join(dirname, './resources/sklearn-model/valid_python_closure/test.pkl')
invalid_pkl_file = os.path.join(dirname, 'resources/sklearn-model/invalid_python_closure/test.txt')
valid_base_path = os.path.join(dirname, 'resources/sklearn-model')
model_config_file_path = os.path.join(dirname,'resources/deployment_api_model_config/sample_model_config.conf')
invalid_model_config_file_path = os.path.join(dirname,'resources/deployment_api_model_config/sample_model_config_invalid.conf')

sample_config = {'name': 'sklearn-model', 'base_path': '/sklearn-model'}

class TestPythonGrpcServer(unittest.TestCase):

	''' defining the functions for the unit test case'''
	def test_get_model_spec_valid(self):
		LOG.info("testing get model spec valid")
		print(model_config_file_path)
		self.assertEqual(sample_config,get_model_spec(model_config_file_path,":"))
		

	def test_get_model_spec_invalid_config_file_path(self):
		LOG.info("testing get model spec invalid config file path")
		with self.assertRaises(FileNotFoundError) as fnf:
			get_model_spec(invalid_model_config_file_path,":")
			self.assertEqual('File Not Found',str(fnf))


	def test_get_model_spec_invalid_delimiter(self):
		self.assertNotEqual(sample_config,get_model_spec(model_config_file_path,"#"))


	def test_load_predict_func_valid(self):
		LOG.info("test load predict function valid file")
		unpickled_file = load_predict_func(valid_pkl_filename)
		self.assertFalse(None,unpickled_file)


	def test_load_predict_func_invalid_file_path(self):
		LOG.info("test load predict function invalid file path")
		with self.assertRaises(FileNotFoundError) as fnf:
			load_predict_func("../test/test2.pkl")
			self.assertEqual('File Not Found',str(fnf))


	def test_load_predict_func_invalid_file(self):
		LOG.info("test load predict function invalid file format , pkl format is not used")
		self.assertRaises(Exception, load_predict_func, invalid_pkl_file)

		
	def test_find_model_version_valid(self):
		LOG.info("test find model version valid valid base path")
		self.assertEqual(str(1),find_model_version(valid_base_path))


	def test_find_model_version_invalid_base_path(self):
		LOG.info("test find model version valid invalid base path")
		with self.assertRaises(ValueError) as cm:
			find_model_version(dirname)
			self.assertEqual('No directory named with number in the model base path to denote the version',str(cm))


if __name__ == "__main__":
  unittest.main()
