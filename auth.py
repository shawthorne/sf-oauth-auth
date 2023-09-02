import os
from dotenv import load_dotenv
from flask import Flask, request, redirect
import requests

load_dotenv()

# Replace these values with your own
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('APP_URL') + ':' + os.getenv('APP_PORT') + '/callback'

app = Flask(__name__)

@app.route('/')
def index():
    # Redirect the user to the Salesforce authorization URL
    url = os.getenv('BASE_SALESFORCE_PRODUCTION_URL') + os.getenv('AUTHORIZE_URL')
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri
    }
    return redirect(url + '?' + requests.compat.urlencode(params))

@app.route('/callback')
def callback():
    # Exchange the authorization code for an access token
    code = request.args.get('code')
    url = os.getenv('BASE_SALESFORCE_PRODUCTION_URL') + os.getenv('TOKEN_URL')
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'code': code
    }
    response = requests.post(url, data=data)
    access_token = response.json()['access_token']
    return 'Access token: ' + access_token

if __name__ == '__main__':
    app.run(port = os.getenv('APP_PORT'))