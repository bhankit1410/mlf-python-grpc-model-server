# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow_serving/apis/prediction_service.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorflow_serving.apis import classification_pb2 as tensorflow__serving_dot_apis_dot_classification__pb2
from tensorflow_serving.apis import get_model_metadata_pb2 as tensorflow__serving_dot_apis_dot_get__model__metadata__pb2
from tensorflow_serving.apis import predict_pb2 as tensorflow__serving_dot_apis_dot_predict__pb2
from tensorflow_serving.apis import regression_pb2 as tensorflow__serving_dot_apis_dot_regression__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow_serving/apis/prediction_service.proto',
  package='tensorflow.serving',
  syntax='proto3',
  serialized_pb=_b('\n0tensorflow_serving/apis/prediction_service.proto\x12\x12tensorflow.serving\x1a,tensorflow_serving/apis/classification.proto\x1a\x30tensorflow_serving/apis/get_model_metadata.proto\x1a%tensorflow_serving/apis/predict.proto\x1a(tensorflow_serving/apis/regression.proto2\x93\x03\n\x11PredictionService\x12\x61\n\x08\x43lassify\x12).tensorflow.serving.ClassificationRequest\x1a*.tensorflow.serving.ClassificationResponse\x12X\n\x07Regress\x12%.tensorflow.serving.RegressionRequest\x1a&.tensorflow.serving.RegressionResponse\x12R\n\x07Predict\x12\".tensorflow.serving.PredictRequest\x1a#.tensorflow.serving.PredictResponse\x12m\n\x10GetModelMetadata\x12+.tensorflow.serving.GetModelMetadataRequest\x1a,.tensorflow.serving.GetModelMetadataResponseB\x03\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[tensorflow__serving_dot_apis_dot_classification__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_predict__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_regression__pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)





DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\370\001\001'))
try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces


  class PredictionServiceStub(object):
    """open source marker; do not remove
    PredictionService provides access to machine-learned models loaded by
    model_servers.
    """

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.Classify = channel.unary_unary(
          '/tensorflow.serving.PredictionService/Classify',
          request_serializer=tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationRequest.SerializeToString,
          response_deserializer=tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationResponse.FromString,
          )
      self.Regress = channel.unary_unary(
          '/tensorflow.serving.PredictionService/Regress',
          request_serializer=tensorflow__serving_dot_apis_dot_regression__pb2.RegressionRequest.SerializeToString,
          response_deserializer=tensorflow__serving_dot_apis_dot_regression__pb2.RegressionResponse.FromString,
          )
      self.Predict = channel.unary_unary(
          '/tensorflow.serving.PredictionService/Predict',
          request_serializer=tensorflow__serving_dot_apis_dot_predict__pb2.PredictRequest.SerializeToString,
          response_deserializer=tensorflow__serving_dot_apis_dot_predict__pb2.PredictResponse.FromString,
          )
      self.GetModelMetadata = channel.unary_unary(
          '/tensorflow.serving.PredictionService/GetModelMetadata',
          request_serializer=tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataRequest.SerializeToString,
          response_deserializer=tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataResponse.FromString,
          )


  class PredictionServiceServicer(object):
    """open source marker; do not remove
    PredictionService provides access to machine-learned models loaded by
    model_servers.
    """

    def Classify(self, request, context):
      """Classify.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def Regress(self, request, context):
      """Regress.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def Predict(self, request, context):
      """Predict -- provides access to loaded TensorFlow model.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def GetModelMetadata(self, request, context):
      """GetModelMetadata - provides access to metadata for loaded models.
      """
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_PredictionServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'Classify': grpc.unary_unary_rpc_method_handler(
            servicer.Classify,
            request_deserializer=tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationRequest.FromString,
            response_serializer=tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationResponse.SerializeToString,
        ),
        'Regress': grpc.unary_unary_rpc_method_handler(
            servicer.Regress,
            request_deserializer=tensorflow__serving_dot_apis_dot_regression__pb2.RegressionRequest.FromString,
            response_serializer=tensorflow__serving_dot_apis_dot_regression__pb2.RegressionResponse.SerializeToString,
        ),
        'Predict': grpc.unary_unary_rpc_method_handler(
            servicer.Predict,
            request_deserializer=tensorflow__serving_dot_apis_dot_predict__pb2.PredictRequest.FromString,
            response_serializer=tensorflow__serving_dot_apis_dot_predict__pb2.PredictResponse.SerializeToString,
        ),
        'GetModelMetadata': grpc.unary_unary_rpc_method_handler(
            servicer.GetModelMetadata,
            request_deserializer=tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataRequest.FromString,
            response_serializer=tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'tensorflow.serving.PredictionService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetaPredictionServiceServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """open source marker; do not remove
    PredictionService provides access to machine-learned models loaded by
    model_servers.
    """
    def Classify(self, request, context):
      """Classify.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def Regress(self, request, context):
      """Regress.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def Predict(self, request, context):
      """Predict -- provides access to loaded TensorFlow model.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def GetModelMetadata(self, request, context):
      """GetModelMetadata - provides access to metadata for loaded models.
      """
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaPredictionServiceStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    """open source marker; do not remove
    PredictionService provides access to machine-learned models loaded by
    model_servers.
    """
    def Classify(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Classify.
      """
      raise NotImplementedError()
    Classify.future = None
    def Regress(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Regress.
      """
      raise NotImplementedError()
    Regress.future = None
    def Predict(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """Predict -- provides access to loaded TensorFlow model.
      """
      raise NotImplementedError()
    Predict.future = None
    def GetModelMetadata(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      """GetModelMetadata - provides access to metadata for loaded models.
      """
      raise NotImplementedError()
    GetModelMetadata.future = None


  def beta_create_PredictionService_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('tensorflow.serving.PredictionService', 'Classify'): tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationRequest.FromString,
      ('tensorflow.serving.PredictionService', 'GetModelMetadata'): tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataRequest.FromString,
      ('tensorflow.serving.PredictionService', 'Predict'): tensorflow__serving_dot_apis_dot_predict__pb2.PredictRequest.FromString,
      ('tensorflow.serving.PredictionService', 'Regress'): tensorflow__serving_dot_apis_dot_regression__pb2.RegressionRequest.FromString,
    }
    response_serializers = {
      ('tensorflow.serving.PredictionService', 'Classify'): tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationResponse.SerializeToString,
      ('tensorflow.serving.PredictionService', 'GetModelMetadata'): tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataResponse.SerializeToString,
      ('tensorflow.serving.PredictionService', 'Predict'): tensorflow__serving_dot_apis_dot_predict__pb2.PredictResponse.SerializeToString,
      ('tensorflow.serving.PredictionService', 'Regress'): tensorflow__serving_dot_apis_dot_regression__pb2.RegressionResponse.SerializeToString,
    }
    method_implementations = {
      ('tensorflow.serving.PredictionService', 'Classify'): face_utilities.unary_unary_inline(servicer.Classify),
      ('tensorflow.serving.PredictionService', 'GetModelMetadata'): face_utilities.unary_unary_inline(servicer.GetModelMetadata),
      ('tensorflow.serving.PredictionService', 'Predict'): face_utilities.unary_unary_inline(servicer.Predict),
      ('tensorflow.serving.PredictionService', 'Regress'): face_utilities.unary_unary_inline(servicer.Regress),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_PredictionService_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('tensorflow.serving.PredictionService', 'Classify'): tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationRequest.SerializeToString,
      ('tensorflow.serving.PredictionService', 'GetModelMetadata'): tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataRequest.SerializeToString,
      ('tensorflow.serving.PredictionService', 'Predict'): tensorflow__serving_dot_apis_dot_predict__pb2.PredictRequest.SerializeToString,
      ('tensorflow.serving.PredictionService', 'Regress'): tensorflow__serving_dot_apis_dot_regression__pb2.RegressionRequest.SerializeToString,
    }
    response_deserializers = {
      ('tensorflow.serving.PredictionService', 'Classify'): tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationResponse.FromString,
      ('tensorflow.serving.PredictionService', 'GetModelMetadata'): tensorflow__serving_dot_apis_dot_get__model__metadata__pb2.GetModelMetadataResponse.FromString,
      ('tensorflow.serving.PredictionService', 'Predict'): tensorflow__serving_dot_apis_dot_predict__pb2.PredictResponse.FromString,
      ('tensorflow.serving.PredictionService', 'Regress'): tensorflow__serving_dot_apis_dot_regression__pb2.RegressionResponse.FromString,
    }
    cardinalities = {
      'Classify': cardinality.Cardinality.UNARY_UNARY,
      'GetModelMetadata': cardinality.Cardinality.UNARY_UNARY,
      'Predict': cardinality.Cardinality.UNARY_UNARY,
      'Regress': cardinality.Cardinality.UNARY_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'tensorflow.serving.PredictionService', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)
