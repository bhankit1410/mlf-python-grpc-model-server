import grpc
import tensorflow_serving.apis.classification_pb2 as tensorflow__serving_dot_apis_dot_classification__pb2
from tensorflow_serving.apis import prediction_service_pb2 as tensorflow__serving_dot_apis_dot_prediction_service__pb2

def run():
    token = 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImxlZ2FjeS10b2tlbi1rZXkiLCJ0eXAiOiJKV1QifQ.eyJqdGkiOiI4Yzk3YWZjM2I4Mzk0N2E5OWVhMjMyNzE3Y2U3ZTFjMyIsInN1YiI6Im1scHRlc3RjbGllbnQiLCJhdXRob3JpdGllcyI6WyJtbHB0ZXN0Y2xpZW50Il0sInNjb3BlIjpbIm1scHRlc3RjbGllbnQiXSwiY2xpZW50X2lkIjoibWxwdGVzdGNsaWVudCIsImNpZCI6Im1scHRlc3RjbGllbnQiLCJhenAiOiJtbHB0ZXN0Y2xpZW50IiwiZ3JhbnRfdHlwZSI6ImNsaWVudF9jcmVkZW50aWFscyIsInJldl9zaWciOiJiNThjNWQ0ZiIsImlhdCI6MTQ4NjYzNDIzMSwiZXhwIjozNjMxMDgyMjMxLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODAvdWFhL29hdXRoL3Rva2VuIiwiemlkIjoidWFhIiwiYXVkIjpbIm1scHRlc3RjbGllbnQiXX0.nIl71Dxktizfb5B870Mlh_-62kN9_Wlda8WYbiz3iFaj22LzIUkQiRIAI57g3IwPXbJnJ1tlrf5_DIJpycRxzfxIZnW_GJW56sgY5L4mdPVHSIUHjeFh5v5tGwmOG6a1mYH_H0y8G-nHNolfSejcyvc4RYvcba4kS2nm-wDKKgfqDVaspM4Ktsa15eLHYn1P0LIUEsewTDm3qL_PgbJC3WKq_qgk02B5Or1n0doLkGBtccYlQEZ9lRixmkdov7_4Nl9UNTPgaYchC0AEaxd_RRCBK78FwC6tw3v1X3xJFXoYdJlMNOnTGdbQ4CVP5-Jd7gifPnUilPPPoJmITg0HZQ'
    metadata = [('authorization', token)]
    channel = grpc.insecure_channel("127.0.0.1:9000")
    stub = tensorflow__serving_dot_apis_dot_prediction_service__pb2.PredictionServiceStub(channel)

    request = tensorflow__serving_dot_apis_dot_classification__pb2.ClassificationRequest()
    request.model_spec.name = "func.pkl"
    request.model_spec.signature_name = "classify_x_to_y"

    example = request.input.example_list.examples.add()
    example.features.feature["sepal length (cm)"].float_list.value.extend([5.1, 7.0, 6.3, 4.6])
    example.features.feature["sepal width (cm)"].float_list.value.extend([3.5, 3.2, 3.3, 3.1])
    example.features.feature["petal length (cm)"].float_list.value.extend([1.4, 4.7, 6.0, 1.5])
    example.features.feature["petal width (cm)"].float_list.value.extend([0.2, 1.4, 2.5, 0.2])

    response = stub.Classify(request)
    print(response)

if __name__ == "__main__":
    run()

