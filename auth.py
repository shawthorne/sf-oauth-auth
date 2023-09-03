import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, redirect, render_template
import requests

# Load environment variables from .env file
load_dotenv()

# Update the .env file with your Salesforce connected app's credentials
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('APP_URL') + ':' + os.getenv('APP_PORT') + '/callback'

# Create a Flask app
app = Flask(__name__)
# Set the port dynamically. Using the default port 5000 causes issues when running the app on a Mac
port_number = os.getenv('APP_PORT')

# Define the default route
@app.route('/')
def index():
    # Render the index.html template
    return render_template("index.html")

# Define the login route
@app.route('/login', methods=('GET', 'POST'))
def login():
    try:
        # Get the environment from the form
        env = request.form['sf_env']
        # Construct the authorization URL based on the users selection
        if env == 'Sandbox':
            url = os.getenv('BASE_SALESFORCE_SANDBOX_URL') + os.getenv('AUTHORIZE_URL')
        else:
            url = os.getenv('BASE_SALESFORCE_PRODUCTION_URL') + os.getenv('AUTHORIZE_URL')
        params = {
            'response_type': 'code',
            'client_id': client_id,
            'redirect_uri': redirect_uri
        }
        #
        return redirect(url + '?' + requests.compat.urlencode(params))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Define the callback route
@app.route('/callback')
def callback():
    try:
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
        # Get the access token from the response
        access_token = response.json()['access_token']
        # Render the success.html template
        return render_template("success.html", token = access_token)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(port=port_number)