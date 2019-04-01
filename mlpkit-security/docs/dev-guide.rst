Developer Guide
===============

We adopt Docker to manage unit tests and integration tests for local development. This docker-compose.yml manages all possible services available in the local dev environment.

Commands
********

First, start all services using

  .. code-block:: bash

    docker-compose up [--build] [-d]

- Force all required docker containers to be built with `--build`
- Start services in background with `-d`

Now four services have started, namely `unit-tests`, `unit-tests-report`, `integration-app`, `integration-tests`. `unit-tests` and `integration-tests` are one-time services that can be re-run if any changes are to be made, whereas `unit-tests-report` and `integration-app` are services that are constantly running in the background.

To run unit tests separately, start a new tab and run command:

  .. code-block:: bash

    docker-compose run unit-tests

After running unit tests, coverage report can be found at http://localhost:8000

To run integration tests separately, use

  .. code-block:: bash

    docker-compose run integration-tests

Finally, stop all services using

  .. code-block:: bash

    docker-compose down




