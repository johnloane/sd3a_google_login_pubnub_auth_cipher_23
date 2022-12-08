import string

from flask import Flask, render_template, session, abort, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
import json
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

import random
import hashlib


import os
import pathlib
import requests

from . import mydb, PB


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://user:password@localhost/your_db'

db = SQLAlchemy(app)



GOOGLE_CLIENT_ID = "877471177663-1546885vr6551jlsdsu8edio3iunejfu.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://sd3aiot23.tk/callback"
)

PB.grant_access("johns-sd3a-pi", True, True)

alive = 0
data = {}


def login_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function()
    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500) #States do not match, Don't trust

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token = credentials._id_token,
        request=token_request,
        audience = GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["google_token"] = credentials._id_token
    return redirect("/secure_area")


@app.route("/logout")
def logout():
    mydb.user_logout(session["google_id"])
    session.clear()
    return redirect("/")


@app.route("/secure_area")
@login_required
def secure_area():
    mydb.add_user_and_login(session['name'], session['google_id'])
    return render_template("index.html", user_id=session['google_id'], online_users=mydb.get_all_logged_in_users())


@app.route('/grant-<user_id>-<read>-<write>', methods=["GET", "POST"])
def grant_access(user_id, read, write):
    if session['google_id'] == '115286914554441662160':
        print("Granting " + user_id + " read: " + read + " write: " + write)
        mydb.add_user_permission(user_id, read, write)
    else:
        print("Non admin trying to grant privileges")
        return json.dumps({"access":"denied"})
    return json.dumps({"access": "granted"})


def salt(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_auth_key():
    s = salt(10)
    hash_string = session['google_id'] + s
    hashing = hashlib.sha256(hash_string.encode('utf-8'))
    return hashing.hexdigest()


@app.route('/get_auth_key', methods=['GET', 'POST'])
def get_auth_key():
    print("Creating authkey for: " + session['google_id'])
    auth_key = create_auth_key()
    mydb.add_auth_key(session['google_id'], auth_key)
    (read, write) = mydb.get_user_access(session['google_id'])
    PB.grant_access(auth_key, read, write)
    auth_response = {'auth_key': auth_key, 'cipher_key': PB.cipher_key}
    json_response = json.dumps(auth_response)
    return str(json_response)








@app.route("/")
def index():
    return render_template("google_login.html")


@app.route("/keep_alive")
def keep_alive():
    global alive, data
    alive += 1
    keep_alive_count = str(alive)
    data['keep_alive'] = keep_alive_count
    parsed_json = json.dumps(data)
    print(parsed_json)
    return str(parsed_json)


if __name__ == '__main__':
    app.run()
