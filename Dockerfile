FROM python:3.6
COPY . .
ENV PYTHONPATH=/
ENV MODELS_CONFIG_FILE_PATH=../test/resources/tensorflow-simple-example/model_config.conf
RUN pip install mlpkit-security/
RUN pip install -r requirements.txt
ENTRYPOINT ["sh", "-c", "/usr/local/bin/python mlfmodelserver/python_grpc_server.py"]