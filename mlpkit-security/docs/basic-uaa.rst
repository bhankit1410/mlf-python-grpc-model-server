=============================
Basic UAA Guide for Developer
=============================

CF UAA Server (DEV)
***************************

**For more detailed API usage, please refer to official** `UAA API Reference`_

.. _UAA API Reference: https://docs.cloudfoundry.org/api/uaa/

Development CF UAA server used in below steps is located at ::

  https://mlp-uaa-integration.cfapps.sap.hana.ondemand.com


Obtain ``admin`` token for client creation
*******************************************

From postman:

- POST to URL `https://mlp-uaa-integration.cfapps.sap.hana.ondemand.com/oauth/token`

- Authorization tab: Set `Type` = `Basic Auth`. `Username` = `mlp.admin`. `Password` = `mlpadminsecret`

- Headers tab: `Content-Type` = `application/json`

- Body tab: `grant_type` = `client_credentials`


  .. code-block:: bash

    curl -X POST \
      "https://mlp-uaa-integration.cfapps.sap.hana.ondemand.com/oauth/token" \
      -H 'authorization: Basic bWxwLmFkbWluOm1scGFkbWluc2VjcmV0' \
      -H 'content-type: application/json' \
      -d grant_type=client_credentials


Use the token from above response to create a test UAA client
***************************************************************

  .. code-block:: bash

    curl -X POST \
      "https://mlp-uaa-integration.cfapps.sap.hana.ondemand.com/oauth/clients" \
      -H 'accept: application/json' \
      -H 'authorization: Bearer %token_generated_from_above_step%' \
      -H 'content-type: application/json' \
      -d '{
      "client_id" : "your_client_id",
      "client_secret" : "your_little_secret",
      "name" : "MLP Sample App",
      "authorities" :  [ %whatever_valid_values_here_which_depends_on_scenario_you_want_to_test%],
      "authorized_grant_types" : [ "client_credentials" ],
      "token_salt" : "6Wlrr7",
      "autoapprove" : true,
      "allowedproviders" : [ "uaa" ],
      "access_token_validity" : 3600
    }
    '

Obtain token using the test client
***********************************

Similar to obtaining admin client. In basic auth, you need to pass in `Username` = `your_client_id` and `Password` = `your_little_secret` instead.

  .. code-block:: bash

    curl -X POST \
      "https://mlp-uaa-integration.cfapps.sap.hana.ondemand.com/oauth/token" \
      -H 'authorization: Basic eW91cl9jbGllbnRfaWQ6eW91cl9saXR0bGVfc2VjcmV0' \
      -H 'content-type: application/json' \
      -d grant_type=client_credentials


  *Do not include* ``token_format=opaque`` *in this request body, otherwise the opaque token returned cannot be validated offline.*
