"""grpc server"""
from concurrent import futures
from datetime import datetime
import os
import sys
import time
import errno
import logging
import threading
import json
import grpc
import tensorflow as tf
import pandas as pd

LOG=logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))
# Disabling this pylint error after checking that this line adheres to
# tensorflow documentation
# pylint: disable=E0611
from tensorflow.python.framework import (
    tensor_util,
    dtypes
)
from mlpkitsecurity import SecurityError
from tensorflow_serving.apis import (
    predict_pb2 as tensorflow__serving_dot_apis_dot_predict__pb2,
    prediction_service_pb2 as tensorflow__serving_dot_apis_dot_prediction_service__pb2,
    classification_pb2 as tensorflow__serving_dot_apis_dot_classification__pb2
)
from mlfmodelserver.token_validator import TokenValidator
from mlfmodelserver.healthcheck import healthcheck_pb2 as healthcheck_dot_healthcheck__pb2, \
    healthcheck_pb2_grpc as healthcheck_dot_healthcheck__pb2__grpc

INPUT_TYPE_BYTES = 0
INPUT_TYPE_INTS = 1
INPUT_TYPE_FLOATS = 2
INPUT_TYPE_DOUBLES = 3
INPUT_TYPE_STRINGS = 4
_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Metric:
    """
    Metric class for abstracting all future metric reporting e.g Prometheus
    """

    def __init__(self, name, model_metrics):
        self.name = name
        self.metrics = model_metrics

    def report(self):
        """
        Log metrics
        """
        LOG.info(self.metrics)


class Servicer(tensorflow__serving_dot_apis_dot_prediction_service__pb2.PredictionServiceServicer):
    """
    class Servicer
    """

    def _Validations(self, request, context):
        try:
            metadata = context.invocation_metadata()

            token_validator = TokenValidator(context, metadata)
            LOG.info("Model Name %s", request.model_spec.name)
            LOG.info("Start of validating token")
            token_result = True#token_validator.validate_token()

            if request.model_spec.name != self.model.model_name:
                LOG.error("Model spec name and model env name does not match")
                context.set_code(grpc.StatusCode.UNIMPLEMENTED)
                raise NotImplementedError('Model spec name and model env does not match' +
                                          str('Model spec name' + request.model_spec.name))
                return False
            if request.model_spec.name is None:
                LOG.error("Model spec name and model env name does not match")
                context.set_code(grpc.StatusCode.UNIMPLEMENTED)
                raise NotImplementedError('Given Model Not Loaded' +
                                          str('Model spec name' + request.model_spec.name))
                return False

            if token_result is True:
                LOG.info('token validated successfully')
                context.set_code(grpc.StatusCode.OK)
                context.set_details(self.model.model_name)
                return True

            return False
        except SecurityError as se:
            s = getattr(se, 'message', str(se))
            raise SecurityError(s)
            return False



    def Classify(self, request, context):
        try:
            example = request.input.example_list.examples[0]

            start_time_millis = self.getCurrentTimeinMillis()
            time_1 = datetime.now()
            if self._Validations(request, context) is True:
                time_2 = datetime.now()

                example = request.input.example_list.examples[0]

                idx = 0
                final_input = []
                final_labels = []
                for k in example.features.feature.keys():
                    v = example.features.feature[k]
                    int_list_value = list(v.int64_list.value)
                    float_list_value = list(v.float_list.value)
                    byte_list_value = list(v.bytes_list.value)

                    if len(int_list_value) > 0:
                        final_input.append(int_list_value)
                        final_labels.append(k)
                    elif len(float_list_value) > 0:
                        final_input.append(float_list_value)
                        final_labels.append(k)
                    elif len(byte_list_value) > 0:
                        final_input.append(byte_list_value)
                        final_labels.append(k)
                    else:
                        LOG.info("Input param empty, ignoring it")
                    idx = idx + 1

                classification_request = pd.DataFrame.from_records(list(zip(*final_input)), columns=final_labels)

                try:
                    classification_outputs = self.model.wrapper_classification_func(classification_request)
                    LOG.info("the output from the model's classification function %s", classification_outputs)
                    response = tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationResponse()

                except grpc.RpcError as grpc_error:
                    end_time_millis = self.getCurrentTimeinMillis()
                    LOG.error("Error while doing Classification")
                    requestDurationInMillis = str(end_time_millis - start_time_millis)
                    self.logRequests(self.model.model_name, requestDurationInMillis, str(0))
                    LOG.error("grpc error : %s", str(grpc_error))
                    s = getattr(grpc_error, 'message', str(grpc_error))
                    raise grpc.RpcError(grpc_error)
                    return None

                classifications = []
                for idx in range(0, classification_request.shape[0]):
                    classes = []
                    classification = tensorflow__serving_dot_apis_dot_classification__pb2.Classifications()
                    for k, v in classification_outputs.items():
                        class_data = tensorflow__serving_dot_apis_dot_classification__pb2.Class()
                        class_data.label = "Class-" + k
                        class_data.score = v[idx]
                        classes.append(class_data)
                    classification.classes.extend(classes)
                    classifications.append(classification)
                response.result.classifications.extend(classifications)

                return response
            else:
                return None
        except Exception as ex:
            s = getattr(ex, 'message', str(ex))
            raise Exception(s)
            return None


    def Predict(self, request, context):
        try:
            start_time_millis = self.getCurrentTimeinMillis()
            time_1 = datetime.now()
            if self._Validations(request, context):
                time_2 = datetime.now()
                predict_request = {}

                for k, v in request.inputs.items():
                    predict_request[k] = tensor_util.MakeNdarray(request.inputs[k])
                    if v.dtype == dtypes.string:
                        predict_request[k] = predict_request[k].astype(str)

                time_3 = datetime.now()

                for k, v in predict_request.items():
                    LOG.info("the key  :%s", k)
                    LOG.info("the value :%s", v)
                # Add the more specific try catch request for predict request

                try:
                    predict_outputs = self.model.wrapper_predict_func(predict_request)
                    LOG.info("the output from the model's predict function %s", predict_outputs)
                    response = tensorflow__serving_dot_apis_dot_predict__pb2.PredictResponse()
                except grpc.RpcError as grpc_error:
                    end_time_millis = self.getCurrentTimeinMillis()
                    LOG.error("Error while doing Prediction")
                    requestDurationInMillis = str(end_time_millis - start_time_millis)
                    self.logRequests(self.model.model_name, requestDurationInMillis, str(0))
                    LOG.error("grpc error : %s", str(grpc_error))
                    s = getattr(grpc_error, 'message', str(grpc_error))
                    raise grpc.RpcError(grpc_error)
                    return None

                for k, v in predict_outputs.items():
                    # Disabling this pylint error after checking that this line adheres to
                    # tensorflow documentation
                    # pylint: disable=E1101
                    response.outputs[k].CopyFrom(tf.contrib.util.make_tensor_proto(v))
                ''' here print the response time taken to serve the request '''

                time_4 = datetime.now()
                end_time_millis = self.getCurrentTimeinMillis()

                validation_time_ms = (time_2 - time_1).microseconds
                parse_time = (time_3 - time_2).microseconds
                handle_time = (time_4 - time_3).microseconds
                model_metrics = {"mlf_mc_model_name": self.model.model_name,
                                 "mlf_mc_token_validation_time_ms": validation_time_ms / 1000,
                                 "mlf_mc_parse_time_ms": parse_time / 1000,
                                 "mlf_mc_handle_time_ms": handle_time / 1000
                                 }
                self.collect_metrics(self.model.model_name, model_metrics)
                requestDurationInMillis = str(end_time_millis - start_time_millis)
                self.logRequests(self.model.model_name, requestDurationInMillis, str(1))
                return response
            else:
                requestDurationInMillis = self.getCurrentTimeinMillis()
                LOG.error("Error while validating JWT token, token not validated successfully")
                self.logRequests(self.model.model_name, requestDurationInMillis, str(0))
                return None

        except Exception as ex:
            s = getattr(ex, 'message', str(ex))
            raise Exception(s)
            return None

    def logRequests(self, model_name, requestDurationInMillis, success):
        current_time = datetime.now().isoformat()
        LOG.info(current_time + " :" + " ModelName: [" + str(model_name) + "] Success: [" + success + "]" +
                 " RequestDurationMillis: [" + str(requestDurationInMillis) + "]")

    def collect_metrics(self, model_name, model_metrics):
        metrics = Metric(model_name, model_metrics)
        metrics.report()

    def getCurrentTimeinMillis(self):
        return int(round(time.time() * 1000))

    def Check(self, request, context):
        # Disabling this pylint error as the healthcheck
        # implementation follows grpc documentation
        # pylint: disable=E1101
        if self.pod_health_status_path:
            ''' Read the readiness/health status from the health status log file'''
            try:
                with open('{}/{}.json'.format(self.pod_health_status_path, self.model_env['model_container_pod_name'])) \
                        as json_file:
                    health_status = json.load(json_file)
                    if health_status['Status'] == '1':
                        return healthcheck_dot_healthcheck__pb2.HealthCheckResponse(status=
                                                                                    healthcheck_dot_healthcheck__pb2.
                                                                                    HealthCheckResponse.ServingStatus.
                                                                                    Name(1))
                    else:
                        return healthcheck_dot_healthcheck__pb2.HealthCheckResponse(status=
                                                                                    healthcheck_dot_healthcheck__pb2.
                                                                                    HealthCheckResponse.ServingStatus.
                                                                                    Name(2))
            except IOError:
                LOG.info("IO Error")
                return healthcheck_dot_healthcheck__pb2.HealthCheckResponse(status=healthcheck_dot_healthcheck__pb2.
                    HealthCheckResponse.ServingStatus.Name(
                    0))
        else:
            return healthcheck_dot_healthcheck__pb2.HealthCheckResponse(status=healthcheck_dot_healthcheck__pb2.
                                                                        HealthCheckResponse.ServingStatus.Name(1))


class ModelContainerBase(object):
    def predict_ints(self, inputs):
        pass

    def predict_floats(self, inputs):
        pass

    def predict_doubles(self, inputs):
        pass

    def predict_bytes(self, inputs):
        pass

    def predict_strings(self, inputs):
        pass


# Inheriting the base class 'Thread'
class AsyncWrite(threading.Thread):
    def  __init__(self, model_env, model_health_status_log, pod_health_status_path):
        # calling superclass init
        threading.Thread.__init__(self)
        self.model_env = model_env
        self.model_health_status_log = model_health_status_log
        self.pod_health_status_path = pod_health_status_path

    def run(self):
        while True:
            with open('{}/{}.json'.format(self.pod_health_status_path,
                                          self.model_env['model_container_pod_name']),
                      mode='w') as outfile:
                print('Updating Container Health Status file ' + self.pod_health_status_path)
                LOG.info("Health status log %s",self.model_health_status_log)
                json.dump(self.model_health_status_log, outfile)

            time.sleep(int(self.model_env['status_exporter_sleep_time']))


class GrpcServer:

    def get_model_health_status(self):
        return self.model_health_status

    def set_model_health_status(self, model_health_status):
        self.model_health_status = model_health_status

    def read_env(self):
        model_env = dict()
        model_env['models_health_base_path'] = os.environ.get('MODELS_HEALTH_BASE_PATH', '/')
        model_env['model_container_id'] = os.environ.get('MODEL_CONTAINER_ID')
        model_env['model_container_pod_name'] = os.environ.get('MODEL_CONTAINER_POD_NAME', 'pod_name')
        model_env['status_exporter_sleep_time'] = os.environ.get('STATUS_EXPORTER_SLEEP_TIME', 60)
        return model_env

    def createhealthstatuslog(self):
        if self.model_env['models_health_base_path'] != '/':
            self.pod_health_status_path = '{}/health/{}'.format(self.model_env['models_health_base_path'],
                                                                self.model_env['model_container_id'])

    def __init__(self):
        self.model_health_status = None
        self.pod_health_status_path = None
        self.model_env = self.read_env()
        self.createhealthstatuslog()

    def start(self, model, port):
        LOG.info("Starting gRPC Server")
        model_env = self.read_env()
        servicer = Servicer()
        servicer.model = model
#        servicer.pod_health_status_path = self.pod_health_status_path
        servicer.model_env = model_env

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        tensorflow__serving_dot_apis_dot_prediction_service__pb2. \
            add_PredictionServiceServicer_to_server(servicer, server)

#        healthcheck_dot_healthcheck__pb2__grpc. \
#            add_HealthServicer_to_server(servicer, server)

#        with open('{}/{}.json'.format(self.pod_health_status_path, self.model_env['model_container_pod_name'])) as outfile:
#            LOG.info('Reading Container Health Status file %s', str(self.pod_health_status_path))
#            LOG.debug("Json file content %s ",str(outfile))
#            self.model_health_status = json.load(outfile)

        server.add_insecure_port("[::]:%s" % port)
        server.start()
        LOG.info('Server started successfully on port: %s ...', str(port))
        LOG.info('Enjoy!')

        if self.pod_health_status_path:
            healthexporter = AsyncWrite(model_env, self.get_model_health_status(),
                                        self.pod_health_status_path)
            healthexporter.start()
            healthexporter.join()

        try:
            while True:
                time.sleep(_ONE_DAY_IN_SECONDS)
        except KeyboardInterrupt:
            server.stop(0)
