import json

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_oidc import OpenIDConnect

import jwt


app = Flask(__name__)
CORS(app)

SECRET_KEY = 'test_secret_key'

app.config.update({
    'SECRET_KEY': SECRET_KEY,
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_OPENID_REALM': 'hysds',
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_TOKEN_TYPE_HINT': 'access_token',
    'OIDC-SCOPES': ['openid']
})


oidc = OpenIDConnect(app)

sa_data = ['sa1', 'sa2', 'sa3']
operator_data = ['operator1', 'operator2', 'operator3']
guest_data = ['guest1']


@app.route('/', methods=['GET'])
def no_token_api():
    return jsonify({
        'results': 'No need for token'
    })


@app.route('/api', methods=['GET'])
@oidc.accept_token(require_token=True)
def test_token_api():
    print(request.headers)

    # auth = request.headers['Authorization']
    # token = auth.split(' ')[1]
    # payload = jwt.decode(token, SECRET_KEY, verify=False)
    # print(json.dumps(payload, indent=2))

    payload = g.oidc_token_info
    print(json.dumps(payload, indent=2))

    roles = payload['realm_access']['roles']

    return jsonify({
        'hello': 'World!!',
        'payload': payload
    })


if __name__ == '__main__':
    app.run(port=5000)
