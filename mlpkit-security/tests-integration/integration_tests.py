#!/usr/bin/python
import os
import unittest
from pprint import pprint
from base64 import b64encode
import json
from urllib.parse import urljoin
import requests

INTEGRATION_APP_BASE_URL = os.environ['INTEGRATION_APP_BASE_URL']
CF_UAA_BASE_URL = os.environ['CF_UAA_BASE_URL']
NEW_ADMIN_CLIENT_ID = "mlp.admin"
NEW_ADMIN_CLIENT_SECRET = "mlp.admin.secret"


class TestCfUaaAuthorize(unittest.TestCase):
    TESTING_URL = urljoin(INTEGRATION_APP_BASE_URL, '_test/')

    @classmethod
    def setUpClass(cls):
        print('Testing endpoints @ ', cls.TESTING_URL)
        # create UAA Admin
        cls.uaac = UaaClientUtil(base_url=CF_UAA_BASE_URL)
        cls.uaac.create_new_admin_client(NEW_ADMIN_CLIENT_ID, NEW_ADMIN_CLIENT_SECRET)
        tk = cls.admin_token = cls.uaac.get_token(NEW_ADMIN_CLIENT_ID,
                                                  NEW_ADMIN_CLIENT_SECRET, scope=None, cache=True)
        # create UAA clients
        cls.uaac.delete_client(tk, "client1")
        cls.uaac.create_client(tk,
                               "client1", "client1secret",
                               ["myxsappname_std!b53.read", "myxsappname_std!b53.write"],
                               ["myxsappname_std!b53.read", "myxsappname_std!b53.write"],
                               "App Client")

        # create model repo UAA clients
        cls.uaac.delete_client(tk, "modelrepo_std!b53_clientid")
        cls.uaac.create_client(tk,
                               "modelrepo_std!b53_clientid", "modelrepo_std!b53_secret",
                               ["modelrepo_std!b53.read", "modelrepo_std!b53.write"],
                               ["modelrepo_std!b53.read", "modelrepo_std!b53.write"],
                               "Model Repo Client")

    def test_service(self):
        token = self.uaac.get_token("client1", "client1secret", scope=None, cache=True)

        r = requests.post(urljoin(self.TESTING_URL, 'svc'),
                          headers={'Authorization': 'Bearer ' + token},
                          data={'scopes': "read"})
        pprint(r.json())
        self.assertEqual(r.status_code, 200)
        self.assertIsNotNone(r.json()['result']['validated token'])
        self.assertIsNotNone(r.json()['result']['new API token'])


class UaaClientUtil:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_token(self, client_id, client_secret, *, scope=None, cache=False):
        url = urljoin(self.base_url, 'oauth/token')
        payload = "grant_type=client_credentials&client_id=" + client_id + "&client_secret=" + client_secret
        if scope is not None:
            payload += "&scope=" + scope
        headers = {
            'content-type': "application/x-www-form-urlencoded"
        }
        if not cache:
            headers['cache-control'] = "no-cache"
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 200:
            raise Exception("Unable to get XS UAA Token for " + client_id + ". Response: " + response.json())
        return response.json()['access_token']

    def create_client(self, token, client_id, client_secret, scopes, authorities="uaa.none", client_name="",
                      access_token_validity=3600):
        url = urljoin(self.base_url, 'oauth/clients')
        print("--------------------------------------------")
        print("Creating new client: " + client_id)
        headers = {
            'authorization': "Bearer " + token,
            'content-type': "application/json"
        }
        body = {
            "scope": scopes,
            "client_id": client_id,
            "client_secret": client_secret,
            "authorized_grant_types": ["client_credentials"],
            "authorities": authorities,
            "name": client_name,
            "access_token_validity": access_token_validity
        }
        response = requests.post(url, headers=headers, data=json.dumps(body))
        if response.status_code == 200 or response.status_code == 201:
            print("create new client successfully. client id=" + client_id)
        elif response.status_code == 409:
            print("client id already exists! client id=" + client_id)
        else:
            print(response.read())
            raise Exception("can not create new client or client id does not exist. client id=" + client_id)

    def create_new_admin_client(self, new_admin_client_id, new_admin_client_secret):
        print("Getting token using default admin client")
        default_admin_token = self.get_token("admin", "adminsecret", cache=True)
        self.create_client(default_admin_token, new_admin_client_id, new_admin_client_secret,
                           [
                               "uaa.admin,clients.read,clients.write,clients.secret,scim.read,scim.write,clients.admin,zones.uaa.admin"],
                           ["clients.read", "clients.secret", "clients.write", "uaa.admin", "clients.admin",
                            "scim.write", "scim.read"],
                           "MLP Admin")

    def delete_client(self, token, client_id):
        url = urljoin(self.base_url, "/oauth/clients/" + client_id)
        print("--------------------------------------------")
        print("Deleting client: " + client_id)
        return requests.delete(url, headers={'authorization': "Bearer " + token})
