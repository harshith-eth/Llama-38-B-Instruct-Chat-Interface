import urllib.request
import json
import os
import ssl
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Define the input data for your model
data = {
    "input_data": {
        "input_string": [
            {"role": "user", "content": "Tell me about AAPL stock."}
        ],
        "parameters": {}
    }
}

body = str.encode(json.dumps(data))

url = os.getenv('AZURE_ML_ENDPOINT')
# Load API key from environment variable
api_key = os.getenv('AZURE_ML_API_KEY')
if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")

# The azureml-model-deployment header will force the request to go to a specific deployment.
# Remove this header to have the request observe the endpoint traffic rules
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + api_key,
    'azureml-model-deployment': 'meta-llama-3-8b-instruct-4'
}

req = urllib.request.Request(url, body, headers)

try:
    response = urllib.request.urlopen(req)

    result = response.read()
    print(result)
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the request ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))
