from flask import Flask, request

from mlpkitsecurity.security import authorize_bs, authorize_fs
from mlpkitsecurity import SecurityError

app = Flask(__name__)


@app.route('/fs')
def simple_endpoint_method_fs():
    fs_name = request.form.get('fs_name')
    access_token = authorize_fs(request=request, fs_name=fs_name)
    return 'authorized! Validated token: {}'.format(access_token)


@app.route('/bs')
def simple_endpoint_method_bs():
    bs_name = request.form.get('bs_name')
    training_name = request.form.get('training_name')
    access_token = authorize_bs(training_name, request=request, bs_name=bs_name)
    return 'authorized! New token: {}'.format(access_token)


@app.errorhandler(SecurityError)
def authorized_exception_handler(error):
    return '{}\n{}'.format(error.detail_info, repr(error.root_cause)), error.code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)