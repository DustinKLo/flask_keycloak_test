from flask import Flask, g, jsonify
from flask_oidc import OpenIDConnect


app = Flask(__name__)

app.config.update({
    'SECRET_KEY': 'dustin_secret_key',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'client_secrets.json',
    'OIDC_OPENID_REALM': 'hysds',
    # 'OIDC_INTROSPECTION_AUTH_METHOD': 'bearer',
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'OIDC_TOKEN_TYPE_HINT': 'access_token',
    'OIDC-SCOPES': ['openid']
})


oidc = OpenIDConnect(app)


@app.route('/', methods=['GET'])
def no_token_api():
    return jsonify({
        'results': 'No need for token'
    })


@app.route('/api', methods=['GET'])
@oidc.accept_token(require_token=True)#, scopes_required=['openid'])
def test_token_api():
    # g.oidc_token_info['sub']
    return jsonify({
        'hello': 'World!!'
    })


if __name__ == '__main__':
    app.run(port=5000)
