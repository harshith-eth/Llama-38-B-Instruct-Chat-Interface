import urllib.request
import json
import os
import ssl
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

def allowSelfSignedHttps(allowed):
    # Bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True) # This line is needed if you use self-signed certificate in your scoring service.

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        input_text = data.get('input_text', '')

        # Define the input data for your model
        payload = {
            "input_data": {
                "input_string": [
                    {"role": "user", "content": input_text}
                ],
                "parameters": {}
            }
        }

        body = str.encode(json.dumps(payload))

        url = os.getenv('AZURE_ML_ENDPOINT')
        api_key = os.getenv('AZURE_ML_API_KEY')
        if not api_key:
            raise Exception("A key should be provided to invoke the endpoint")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + api_key,
            'azureml-model-deployment': 'meta-llama-3-8b-instruct-4'
        }

        req = urllib.request.Request(url, body, headers)

        response = urllib.request.urlopen(req)
        result = response.read().decode('utf-8')
        result_json = json.loads(result)

        return jsonify(result_json)

    except urllib.error.HTTPError as error:
        return jsonify({
            "error": {
                "status_code": error.code,
                "headers": str(error.info()),
                "body": error.read().decode("utf8", 'ignore')
            }
        }), error.code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
