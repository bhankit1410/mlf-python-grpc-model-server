================
XS UAA Auth Flow
================

Environment Variables
*********************
  There are currently 4 environment variables required for doing token validation.

  ==============================================  ===============================================================
  Environment Variable                            Remarks
  ==============================================  ===============================================================
  ``MLP_USE_XSUAA``                               Set this variable to `true` to enable XSUAA auth flow
  ``MLP_UAA_PUBLIC_KEY`` or ``MLP_UAA_BASE_URL``  UAA public key to validate token or UAA server URL to retrieve the public key
  ``MLP_MLSERVICE_XSAPPNAME``                     XS App Name of the application, e.g. foundation!b87
  ``MLP_MLSERVICE_DEFAULT_SCOPES``                Default auth scopes (optional, comma-separated). If expected default scopes are `<xsappname>.read` and `<xsappname>.write` then `MLP_MLSERVICE_DEFAULT_SCOPES=read,write`
  ==============================================  ===============================================================

  If app is bound to an XSUAA master instance, you no longer required to specify 'MLP_MLSERVICE_XSAPPNAME', 'MLP_UAA_PUBLIC_KEY', and 'MLP_UAA_BASE_URL'

  ==============================================  ===============================================================
  Environment Variable                            Remarks
  ==============================================  ===============================================================
  ``MLP_USE_XSUAA``                               Set this variable to `true` to enable XSUAA auth flow
  ``MLP_XSUAA_SERVICE_INSTANCE_NAME``             XSUAA master instance name bound to the app. MLP_UAA_PUBLIC_KEY and MLP_MLSERVICE_XSAPPNAME will be populated from its VCAP_SERVICES.
  ``MLP_MLSERVICE_DEFAULT_SCOPES``                Default auth scopes (optional, comma-separated). If expected default scopes are `<xsappname>.read` and `<xsappname>.write` then `MLP_MLSERVICE_DEFAULT_SCOPES=read,write`
  ==============================================  ===============================================================

  Refer to:

- `ML Foundation Service Broker docs <https://github.wdf.sap.corp/ICN-ML/ml-foundation-servicebroker>`_.
- `XSUAA guide <https://wiki.wdf.sap.corp/wiki/display/MLPdev/2017/05/31/Migration+to+XSUAA+POC+for+SAP+Leornado+ML+Foundation++Services>`_ for configuration.

Sample snippet for use in ML services
*************************************

  .. code-block:: python

    import logging
    import sys
    from flask import Flask, request, jsonify
    from mlpkitsecurity.xs_auth import authorize
    from mlpkitsecurity.token_utils import retrieve_foundation_service_token
    from mlpkitsecurity import SecurityError

    app = Flask(__name__)
    LOG = logging.getLogger(__name__)
    LOG.setLevel(logging.INFO)
    LOG.addHandler(logging.StreamHandler(stream=sys.stdout))

    @app.route('/my_service', methods=['POST'])
    def sample_service():
        # pass scopes if you need to validate token against different scopes.
        # e.g. authorize(request=request, scopes=['other_scope'])
        valid_client_id = authorize(request=request)


        # get foundation service access token
        foundation_service_access_token = retrieve_foundation_service_token()

        # use `foundation_service_access_token` to access `my_model` in model repository

        return 'some_response'

    @app.errorhandler(SecurityError)
    def handle_error(error):
        # handle `SecurityError`
        response = jsonify({'message': error.detail_info})
        response.status_code = error.code
        return response


  Client is expected to send POST request to `/my_service` that includes below headers:

  ================================ ================================
  Headers                          Value Descriptions
  ================================ ================================
  Authorization                    Bearer ``your_non-opaque_token``
  ================================ ================================

