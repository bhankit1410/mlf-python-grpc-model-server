from flask import Flask, request
from mlpkitsecurity.cf_auth import authorize
from mlpkitsecurity import SecurityError


app = Flask(__name__)


@app.route('/svc')
def simple_endpoint_method():
    access_token = authorize(request)
    return 'authorized! Validated token: {}'.format(access_token)


@app.errorhandler(SecurityError)
def authorized_exception_handler(error):
    return '{}\n{}'.format(error.detail_info, repr(error.root_cause)), error.code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
