import requests
import json
import time

# 1. Login to get our local access token
login_res = requests.post("http://api_gateway/auth/login", data={"username": "test2@test.com", "password": "test123"})
if login_res.status_code != 200:
    print("Login failed:", login_res.text)
    exit(1)
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. To get a sandbox public token, we can use the Plaid API directly
import plaid
from plaid.api import plaid_api
import os
from plaid.model.sandbox_public_token_create_request import SandboxPublicTokenCreateRequest
from plaid.model.sandbox_public_token_create_request_options import SandboxPublicTokenCreateRequestOptions
from plaid.model.products import Products

config = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID'),
        'secret': os.getenv('PLAID_SECRET'),
    }
)
client = plaid_api.PlaidApi(plaid.ApiClient(config))
try:
    pt_req = SandboxPublicTokenCreateRequest(
        institution_id="ins_109508", # First Platypus Bank
        initial_products=[Products("transactions"), Products("investments")],
    )
    pt_res = client.sandbox_public_token_create(pt_req)
    public_token = pt_res['public_token']
    print(f"Got sandbox public token: {public_token}")
    
    # 3. Exchange with our backend
    print("Exchanging via local backend endpoint...")
    backend_res = requests.post("http://api_gateway/ingestion/plaid/set_access_token", headers=headers, json={"public_token": public_token})
    print(f"Backend status code: {backend_res.status_code}")
    print(f"Backend response: {backend_res.text}")
except Exception as e:
    print("Error:", e)
