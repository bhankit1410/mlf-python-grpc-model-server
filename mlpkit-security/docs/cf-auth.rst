================
CF UAA Auth Flow
================

Environment Variables
*********************
  There are currently 2 environment variables required for doing token validation.

  =====================================  =====================================================================================================================================
  Environment Variable                    Remarks
  =====================================  =====================================================================================================================================
  ``CLEA_UAA_SERVER_BASE_URL``           Base URL of CF UAA used for token validation.
  ``CLEA_UAA_USE_GLOBAL_TENANT``         if set to true, token validation will check globalTenantName header. Otherwise, token validation will always check tenantName header.
  =====================================  =====================================================================================================================================

  *If any of these not set, warnings will be logged during module import and exceptions will be raised at runtime.*

Sample snippet for use in ML services
*************************************

  .. code-block:: python

    import logging
    import sys
    from flask import Flask, request, jsonify
    from mlpkitsecurity.cf_auth import authorize
    from mlpkitsecurity import SecurityError

    app = Flask(__name__)
    LOG = logging.getLogger(__name__)
    LOG.setLevel(logging.INFO)
    LOG.addHandler(logging.StreamHandler(stream=sys.stdout))

    @app.route('/my_service', methods=['POST'])
    def sample_service():
        access_token = authorize(request=request)

        # returned `access_token` is the same as one in `request`

        return 'some_response'

    @app.errorhandler(SecurityError)
    def handle_error(error):
        # handle `SecurityError`
        response = jsonify({'message': error.detail_info})
        response.status_code = error.code
        return response

  Client is expected to send POST request to `/my_service` that includes below headers:

  ================================== =============================================================
  Headers                            Value Descriptions
  ================================== =============================================================
  Authorization                      Bearer ``your_non-opaque_token``
  globalTenantName                   Tenant name, if CLEA_UAA_USE_GLOBAL_TENANT set to true
  tenantName                         Tenant name, if CLEA_UAA_USE_GLOBAL_TENANT is not set to true
  ================================== =============================================================

