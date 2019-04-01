#!/usr/bin/python
from flask import Flask, request, jsonify
import logging
import sys
from mlpkitsecurity.xs_auth import authorize
from mlpkitsecurity.token_utils import retrieve_foundation_service_token

app = Flask(__name__)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(stream=sys.stdout))


@app.route('/_test/svc', methods=['POST'])
def sample_service():
    # validate scopes
    scopes_params = request.form.get('scopes')
    scopes = scopes_params.split(",") if scopes_params else None
    access_token = authorize(request=request, scopes=scopes)

    # retrieve token for a given service broker instance
    new_token = retrieve_foundation_service_token()
    
    return jsonify({'result': {'validated token': access_token,
                               'new API token': new_token
                               }
                    })


@app.errorhandler(Exception)
def handle_error(error):
    response = jsonify({'detail_info': getattr(error, 'detail_info', repr(error)), 'root_cause': repr(getattr(error, 'root_cause', ''))})
    response.status_code = error.code
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
