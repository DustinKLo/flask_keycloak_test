Testing out Keycloak authentication in a Flask Rest API
https://www.keycloak.org/

#### Activate virtual environment
```
# Preferably python3
$ virtualenv env

$ source env/bin/activate
$ pip install -r requirements.txt
```

#### Starting Keycloak server
```
$ ./standalone.sh
```

###### Access the admin console through `http://localhost:8080`
![Admin console](./img/admin_console.png)

###### Adding the Realm in Keycloak
![Add realm](./img/add_realm.png)

###### Create Client in Keycloak admin called Mozart
- Make sure `Access Type` is `confidential`
![Create Client](./img/mozart_access_type.png)

###### Create Realm roles through the admin
![Create Role](./img/roles.png)

###### Create User in the realm then map the roles to the user
![Map roles to user](./img/role_mappings.png)

#### Filling in client_secrets.json with parameters from Keycloak
`client_secret` can be retrieved in the admin page for the `Mozart` client
![Mozart client secret](./img/client_secret.png)
```
{
  "web": {
    "issuer": "http://localhost:8080/auth/realms/hysds",
    "auth_uri": "http://localhost:8080/auth/realms/hysds/protocol/openid-connect/auth",
    "client_id": "mozart",
    "client_secret": "<client secret from keycloak client>",
    "redirect_uris": [
      "http://localhost:5000/*"
    ],
    "userinfo_uri": "http://localhost:8080/auth/realms/hysds/protocol/openid-connect/userinfo",
    "token_uri": "http://localhost:8080/auth/realms/hysds/protocol/openid-connect/token",
    "token_introspection_uri": "http://localhost:8080/auth/realms/hysds/protocol/openid-connect/token/introspect",
    "bearer_only": "true"
  }
}
```

#### Start Flask app
```
# separate tab
$ flask run
```

#### Getting auth token from Keycloak
```
$ export USERNAME=username
$ export PASSWORD=password
$ export CLIENT_SECRET=<client secret from Keycloak>

$ export AUTH_TOKEN=`curl -s \
  -d "client_id=mozart" -d "client_secret=$CLIENT_SECRET" \
  -d "username=$USERNAME" -d "password=$PASSWORD" \
  -d "grant_type=password" \
  "http://localhost:8080/auth/realms/hysds/protocol/openid-connect/token" | jq -r '.access_token'`

$ echo $AUTH_TOKEN
eyJhbGciOiJSUzI...cdsh5qONTHr7tsfOiKWSA5fscWaQ
```

#### Testing out Flask API endpoints
```
# returns 401 because /api endpoint is secured
$ curl -s http://localhost:5000/api | jq
{
  "error": "invalid_token",
  "error_description": "Token required but invalid"
}

$ curl -s -H "Authorization: Bearer $AUTH_TOKEN" http://localhost:5000/api | jq
{
  "hello": "World!!",
  "payload": {
    "acr": "1",
    "active": true,
    "allowed-origins": [
      "*"
    ],
    "aud": "account",
    "azp": "mozart",
    "client_id": "mozart",
    "email": "d1073601@yahoo.com",
    "email_verified": true,
    "exp": 1598489834,
    "family_name": "lo",
    "given_name": "dustin",
    "iat": 1598486234,
    "iss": "http://localhost:8080/auth/realms/hysds",
    "jti": "727e6888-a2b5-44e0-b2e4-ce07b04367ae",
    "name": "dustin lo",
    "preferred_username": "username",
    "realm_access": {
      "roles": [
        "operator",
        "sa"
      ]
    },
    "resource_access": {
      "account": {
        "roles": [
          "manage-account",
          "manage-account-links",
          "view-profile"
        ]
      }
    },
    "scope": "profile email",
    "session_state": "9cf2b2da-691a-4cda-bcc8-a858a67b7fb3",
    "sub": "0db437a6-aed2-4cce-8aa1-248142dce5d9",
    "typ": "Bearer",
    "username": "username"
  }
}
```

*Note: flask-oidc allows users to also pass in tokens through query parameters (handled in `request.args`)*
[flask-oidc source code](https://github.com/puiterwijk/flask-oidc/blob/master/flask_oidc/__init__.py#L880-L885)
```
curl "http://localhost:5000/api?access_token=$AUTH_TOKEN" | jq
{
  "hello": "World!!",
  .
  .
  .
}
```
