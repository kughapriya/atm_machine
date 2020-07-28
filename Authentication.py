from api.tests import BaseTestCase
from flask_restful import Resource
from api import rest_api, 
from api.utils import auth
from api.config import load_config
from unittest import mock
import json
import datetime


class AuthenticationATMTestSuite(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.headers = {"Content-Type": "application/json"}
        self.account = {
            "account_number": "11223344",
            "pin": "1234",
            "first_name": "John",
            "last_name": "Doe",
            "opening_balance": 100000
        }
        self.login = {"account_number": self.account["account_number"],
                      "pin": self.account["pin"]}

        # create account
        self.client.post("/accounts/create",
                         data=json.dumps(self.account),
                         headers=self.headers)

    def create_protected_endpoint(self):
       
        class ProtectedEndpoint(Resource):
            @auth
            def get(self):
                return "Lorem ipsum sit dolor amet"
        rest_api.resources = []
        rest_api.add_resource(ProtectedEndpoint, "/protected_resource")
        self.app = create_app(load_config())
        self.client = self.app.test_client()

    def test_can_login(self):
       
        response = self.client.post("/accounts/login",
                                    data=json.dumps(self.login),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.get_data())
        self.assertIn("token", data)

    def test_login_with_non_existent_account_number(self):
       
        self.login["account_number"] = "non-existent"
        response = self.client.post("/accounts/login",
                                    data=json.dumps(self.login),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 401)

        data = json.loads(response.get_data())
        self.assertEqual(data, {"message": "Invalid account number."})

    def test_login_with_invalid_pin(self):
        
        self.login["pin"] = "0000"
        response = self.client.post("/accounts/login",
                                    data=json.dumps(self.login),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 401)

        data = json.loads(response.get_data())
        self.assertEqual(data, {"message": "Pin is invalid."})

    def test_access_protected_endpoint_without_authorization(self):
        
        self.create_protected_endpoint()
        response = self.client.get("/protected_resource")
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.get_data())
        self.assertEqual(data, {'message': {
                         'Authorization': "Authorization token required. Hint:"
                         " Make sure you're using the 'Bearer' schema."}})

    def test_auth_token_expires(self):
        
        self.create_protected_endpoint()

        
        response = self.client.post("/accounts/login",
                                    data=json.dumps(self.login),
                                    headers=self.headers)
        self.assertEqual(response.status_code, 200,
                         msg="Unable to retrieve authentication token.")
        token = json.loads(response.get_data())["token"]

        
        with mock.patch("jwt.api_jwt.datetime", autospec=True) as mock_time:
            """
            Set current time to future to simulate token use after expiry
            has passed
            """
            mock_time.utcnow.return_value = datetime.datetime.utcnow() +\
                datetime.timedelta(hours=20)
            self.headers["Authorization"] = "Bearer " + token
            response = self.client.get("/protected_resource",
                                       headers=self.headers)
            self.assertEqual(response.status_code, 401)

            data = json.loads(response.get_data())
            self.assertEqual(data, {'message': {"Authorization":
                             "Token Expired. Please log in again."}})
