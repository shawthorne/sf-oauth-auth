# Salesforce API Authorization using Python

## Overview

This tutorial provides step-by-step instructions to receive an Access Token from Salesforce using the [OAuth 2.0 Web Server Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm&type=5). This token can be used to call various Salesforce APIs.

You can find many tutorials that use a username-password flow for authentication, but this is not safe, nor would you use this in any real project. In fact, Salesforce has started blocking this by default ([Block Authorization Flows to Improve Security](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_disable_username_password_flow.htm&type=5)).

This tutorial uses [Python3](https://www.python.org/) along with the [Flask](https://flask.palletsprojects.com/en/2.3.x/) framework and [Requests](https://requests.readthedocs.io/en/latest/) package.

## Prerequisites

1. Access to a Salesforce Sandbox or Dev Org
2. The latest version of Python3 installed locally
3. Visual Studio Code installed

## Step By Step

### Create a Connected App in Salesforce

1. Setup\\App Manager
2. New Connected App
3. Connected App Name = API Test
4. API Name = API\_Test
5. Contact Email = your email
6. Enable OAuth Settings = checked
7. Callback URL = `http://localhost:7777/callback`
8. Available OAuth Scopes - Select
	1. Manage user data via APIs (api)
	2. Perform requests at any time (refresh\_token, offline\_access)
	3. Manage user data via Web browsers (web)
9. Click Save

### Create a Service Account (User) in Salesforce

1. Create a Profile (we will use the Salesforce Integration User License)
	1. Clone the Salesforce API Only System Integrations
	2. Name = Service API User
2. Create a Permission Set
	1. Name = Service API Permission Set
	2. License = Salesforce API Integration
	3. Edit the Object Settings and grant Read Access to Accounts
	4. Under Field Permissions, check Read Access for all fields
	5. Save the changes
3. Create a User
	1. Setup\\Users
	2. New User
	3. First Name = API
	4. Last Name = User
	5. Email = your email
	6. Username = Something unique, like `api.user@test.not`
	7. User License = Salesforce Integration
	8. Profile = Service API User
	9. Active = checked
	10. Time Zone = your time zone
	11. Check “Generate new password…”
	12. Click Save
	13. Assign the Service API Permission Set to the User
	14. Save
4. Set a Password
	1. You will receive an email with a link to set your password
	2. Save the username and password somewhere safe

### Grant the user access to the connected app

1. View the connected app, click Manage then Edit Policies
2. Change Permitted Users from All users may self-authorize to Admin approved users are pre-authorized and click Save
3. Scroll down to Profiles and click Manage Profiles
4. Add the Profile assigned to your API User (Service API User)

### Create a new Directory and Populate with Core Files

1. Create a new Directory (wherever you choose) named sf-oauth-auth
2. Change to the new directory
3. Open Visual Studio Code
4. Open the Folder sf-oauth-auth (File\\Open Folder)

### Create a Virtual Environment

1. In Visual Studio Code, open the Command Pallet (Command Shift P)
2. Choose Python: Create Environment
3. Choose Venv
4. Choose the latest version of Python3 installed
5. Open a new Terminal and verify you are in the virtual environment

<img width="724" alt="1" src="https://github.com/shawthorne/sf-oauth-auth/assets/2444943/d7cdf91a-d7b4-45ec-8ffa-d2f6b86fa723">

### Create Files and Folders
1. Create a new File - auth.py
2. Create a new File - .env
3. Create a new Folder - templates
4. In the Templates Folder
	1. Create a new File - index.html
	2. Create a new File - success.html

### Add Code
1. Open auth.py
2. Paste in this code
```python
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
        # Redirect the user to the authorization URL
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
```
3. Open index.html
4. Paste in this markup
```html
<!DOCTYPE html>
<html lang="en">
   <head>
      <title>SF OAUTH AUTH</title>
    </head>
   <body>
      <form action = "login" method = "post">
         <p>Select Salesforce Environment</p>
         <p>
            <select name = "sf_env" id="sf_env">
                <option value="Production">Production</option>
                <option value="Sandbox">Sandbox</option>
                <option value="Dev">Dev</option>
              </select>
         </p>
         <p><input type = "submit" value = "Submit" /></p>
      </form>
   </body>
</html>
```
5. Open success.html
6. Paste in this markup
```html
<!DOCTYPE html>
<html lang="en">
   <head>
      <title>SF OAUTH AUTH</title>
    </head>
   <body>
    <h1>You have successfully logged in!</h1>
    <h2>Salesforce returned this token: {{ token }}</h2>
   </body>
</html>
```
7. Open .env
8. Paste in this text
```plain text
CLIENT_ID = 
CLIENT_SECRET = 
APP_URL = http://localhost
APP_PORT = 7777
BASE_SALESFORCE_PRODUCTION_URL = https://login.salesforce.com
BASE_SALESFORCE_SANDBOX_URL = https://test.salesforce.com
AUTHORIZE_URL = /services/oauth2/authorize
TOKEN_URL = /services/oauth2/token
```
9. Copy your credentials from your Salesforce Connected App
10. View the Connected App
11. Click Manage Consumer Details
12. Copy Consumer Key
13. Paste it after CLIENT_ID =
14. Copy Consumer Secret
15. Paste it after CLIENT_SECRET =
16. Make sure you have Saved all the files above

### Import Python Packages
1. Open a new Terminal in Visual Studio Code
2. Type/Paste this text
```bash
pip3 install flask, requests, python-dotenv
```
3. Press Enter
4. Assuming there are no errors, you are ready to test
## Test
1. Right-Click the auth.py file and click Run Python File in Terminal
2. Open a new browser window and navigate to [http://127.0.0.1:7777](http://127.0.0.1:7777)
3. Choose the Salesforce org type that you are using
4. Click Submit
5. Enter the Username and Password for your API User created above
6. Click Log In
7. Assuming there are no errors, you will see our success.html page will open with a message: “You have successfully logged in! Followed by the returned token.
8. You can now use this token to authenticate against api calls to Salesforce.
9. To quit the program, go back to the terminal and click Control C

## References
1. [Flask Documentation](https://flask.palletsprojects.com/en/2.3.x/)
2. [Requests Documentation](https://pypi.org/project/requests/)
3. [OAuth 2.0 Web Server Flow](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm&type=5)
4. [Connected Apps](https://help.salesforce.com/s/articleView?id=sf.connected_app_overview.htm&type=5)
5. [Github Repo with Complete Project](https://github.com/shawthorne/sf-oauth-auth)
