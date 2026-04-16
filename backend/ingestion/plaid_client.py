import os
import plaid
from plaid.api import plaid_api

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID', 'placeholder_client_id')
PLAID_SECRET = os.getenv('PLAID_SECRET', 'placeholder_secret')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')

configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox if PLAID_ENV == 'sandbox' else plaid.Environment.Development,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)

api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)
