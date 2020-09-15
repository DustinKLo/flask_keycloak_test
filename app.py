import json
from functools import wraps

from flask import Flask, g, jsonify, request
from flask_cors import CORS
from flask_oidc import OpenIDConnect


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


class NewOpenIDConnect(OpenIDConnect):
    def accept_token_modified(self, require_token=False, scopes_required=None, render_errors=True):
        def wrapper(view_func):
            @wraps(view_func)
            def decorated(*args, **kwargs):
                """
                this method is pretty much the same as the accept_token provided in the parent class with a small change
                if there's a specific header (ie. X-FORWARDED-HOST), then we'll let flask-oidc authenticate
                if not, we can skip the authentication step and proceed
                """
                print('HEADERS ############################################')
                print(request.headers)

                if True:  # will add logic later, but this is where we check if we authenticate or not
                    print("Skip authenticating...")
                    return view_func(*args, **kwargs)

                print("request coming through proxy, authenticating...")
                token = None
                if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
                    token = request.headers['Authorization'].split(None,1)[1].strip()
                if 'access_token' in request.form:
                    token = request.form['access_token']
                elif 'access_token' in request.args:
                    token = request.args['access_token']

                validity = self.validate_token(token, scopes_required)
                if (validity is True) or (not require_token):
                    return view_func(*args, **kwargs)
                else:
                    response_body = {
                        'error': 'invalid_token',
                        'error_description': validity
                    }
                    if render_errors:
                        response_body = json.dumps(response_body)
                    return response_body, 401, {'WWW-Authenticate': 'Bearer'}
            return decorated
        return wrapper


# oidc = OpenIDConnect(app)
oidc = NewOpenIDConnect(app)


@app.route('/', methods=['GET'])
def no_token_api():
    return jsonify({
        'results': 'No need for token'
    })


@app.route('/api/test', methods=['GET'])
@oidc.accept_token(require_token=True)
def test_token_api():
    print('HEADERS ############################################')
    print(request.headers)
    payload = g.oidc_token_info
    print(json.dumps(payload, indent=2))

    return jsonify({
        'success': True,
        'payload': payload
    })


@app.route('/api/optional', methods=['GET'])
@oidc.accept_token_modified(require_token=True)
def test_optional_token():
    return jsonify({
        'success': True,
        "message": "testing the /api/optional endpoint"
    })


if __name__ == '__main__':
    app.run(port=5000)
