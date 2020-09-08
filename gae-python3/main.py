from flask import Flask, render_template, request
from google.auth.transport import requests as reqs
from google.oauth2 import id_token
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    audience = "https://example.com"
    token = id_token.fetch_id_token(reqs.Request(), audience)

    response = "Google-signed ID Token for audience '%s': %s\n" % (audience, token)
    response += "Google certificate: https://www.googleapis.com/oauth2/v1/certs\n"
    return response, 200, {'Content-type': 'text/plain'}


if __name__ == '__main__':
    # This is used when running locally only. 
    app.run(host='127.0.0.1', port=8080, debug=True)
