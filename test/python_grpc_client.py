import grpc
from tensorflow_serving.apis import predict_pb2 as tensorflow__serving_dot_apis_dot_predict__pb2
from tensorflow_serving.apis import prediction_service_pb2 as tensorflow__serving_dot_apis_dot_prediction_service__pb2
import tensorflow as tf

def run():
    token = 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiI4Yzk3YWZjM2I4Mzk0N2E5OWVhMjMyNzE3Y2U3ZTFjMyIsInN1YiI6Im1scHRlc3RjbGllbnQiLCJhdXRob3JpdGllcyI6WyJtbHB0ZXN0Y2xpZW50Il0sInNjb3BlIjpbIm1scHRlc3RjbGllbnQiXSwiY2xpZW50X2lkIjoibWxwdGVzdGNsaWVudCIsImNpZCI6Im1scHRlc3RjbGllbnQiLCJhenAiOiJtbHB0ZXN0Y2xpZW50IiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiJiNThjNWQ0ZiIsImlhdCI6MTQ4NjYzNDIzMSwiZXhwIjozNjMxMDgyMjMxLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvdWFhL29hdXRoL3Rva2VuIiwiemlkIjoidWFhIiwiYXVkIjpbIm1scHRlc3RjbGllbnQiXX0.nIl71Dxktizfb5B870Mlh_-62kN9_Wlda8WYbiz3iFaj22LzIUkQiRIAI57g3IwPXbJnJ1tlrf5_DIJpycRxzfxIZnW_GJW56sgY5L4mdPVHSIUHjeFh5v5tGwmOG6a1mYH_H0y8G-nHNolfSejcyvc4RYvcba4kS2nm-wDKKgfqDVaspM4Ktsa15eLHYn1P0LIUEsewTDm3qL_PgbJC3WKq_qgk02B5Or1n0doLkGBtccYlQEZ9lRixmkdov7_4Nl9UNTPgaYchC0AEaxd_RRCBK78FwC6tw3v1X3xJFXoYdJlMNOnTGdbQ4CVP5-Jd7gifPnUilPPPoJmITg0HZQ'
    metadata = [('authorization', token)]

    options = (('grpc.ssl_target_name_override',
                    'model-from-source.default.example.com',),)

    channel = grpc.insecure_channel('localhost:31380',options=options) 
    stub = tensorflow__serving_dot_apis_dot_prediction_service__pb2.PredictionServiceStub(channel)

    request = tensorflow__serving_dot_apis_dot_predict__pb2.PredictRequest()
    request.model_spec.name = 'tensorflow-feature-sum-model'
    request.model_spec.signature_name = "tensorflow-feature-sum-model"
    request.model_spec.version.value = 1

    # dataframe columns admit, gre, gpa, rank
    # https://stats.idre.ucla.edu/r/dae/logit-regression/
    request.inputs["X"].CopyFrom(
        tf.contrib.util.make_tensor_proto([1, 45.4, 4, 10], shape=[4]))
    response = stub.Predict(request)
    print(response)

if __name__ == "__main__":
    run()