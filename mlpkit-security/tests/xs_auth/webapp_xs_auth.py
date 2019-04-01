from flask import Flask, request

from mlpkitsecurity.xs_auth import authorize
from mlpkitsecurity import SecurityError

app = Flask(__name__)


@app.route('/authorize')
def simple_endpoint_method_authorize():
    xs_app_name = request.form.get('xs_app_name')
    scopes_params = request.form.get('scopes')
    scopes = scopes_params.split(",") if scopes_params else None
    access_token = authorize(request=request, xs_app_name=xs_app_name, scopes=scopes) \
        if xs_app_name else authorize(request=request, scopes=scopes)
    return 'authorized! Validated token: {}'.format(access_token)


@app.errorhandler(SecurityError)
def authorized_exception_handler(error):
    return '{}\n{}'.format(error.detail_info, repr(error.root_cause)), error.code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)