import logging
import requests

from flask import Flask


app = Flask(__name__)


@app.route('/')
def index():
    try:
        r = requests.get(
            'http://metadata/computeMetadata/v1/instance/service-accounts/default/identity?audience=https%3A%2F%2Fexample.com%2F',
            headers={'Metadata-Flavor': 'Google'},
            timeout=2)
        return "ID Token %s" % r.text
        
    except requests.RequestException:
        logging.info('Metadata server could not be reached, assuming local.')
        return 'localhost'

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)