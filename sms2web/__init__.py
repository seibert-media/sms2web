#!/usr/bin/env python3

import sys
from math import floor
from os import environ, getcwd
from os.path import dirname, realpath, join
from flask import Flask, render_template, request, session, Response
from datetime import datetime
from time import time
from subprocess import check_output, CalledProcessError
import json

sys.path.insert(0, realpath(join(getcwd(), dirname(__file__))))

import google_auth
from lib import init_db, select, insert

app = Flask(__name__)
app.secret_key = environ.get("FLASK_SECRET_KEY", default='test')
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SEND_FILE_MAX_AGE_DEFAULT=300,
)
app.register_blueprint(google_auth.app)

with app.app_context():
    init_db()


@app.route('/', methods = ['GET'])
@google_auth.required
def home():
    since = int(request.args.get('since', 0))
    per_page = int(request.args.get('per_page', 12))
    page = int(request.args.get('page', 0))
    offset = page*per_page
    total = select('''SELECT COUNT(ROWID) AS count FROM "sms"''')[0]['count']
    last_page = floor(total / per_page)
    layout = request.args.get('layout') != 'false'
    sms_list = select(
        '''
            SELECT * FROM sms
            WHERE timestamp > :timestamp
            ORDER BY timestamp DESC
            LIMIT :limit
            OFFSET :offset
        ''',
        timestamp=since,
        offset=offset,
        limit=per_page,
    )

    return render_template(
        "home.html",
        sms_list=sms_list,
        page=page,
        per_page=per_page,
        last_page=last_page,
        datetime=datetime,
        allowlist_url=environ.get("ALLOWLIST_URL", default=False),
        help_url=environ.get("HELP_URL", default=False),
        numbers=environ.get("NUMBERS", default=False),
        user=session['google_user'],
        layout=layout,
    )


@app.route('/sms77', methods=['POST'])
def sms77():
    # {"webhook_event":"sms_mo","webhook_timestamp":"2021-05-04T13:15:12+02:00","data":{"id":800342,"sender":"491702607871","time":1620126912,"text":"Test","system":"4915735990598"}}
    sms = {
        'sender': request.get_json()['data']['sender'],
        'message': request.get_json()['data']['text'],
        'timestamp': int(request.get_json()['data']['time']),
        'received_at': int(time()),
    }
    insert(
        '''
            INSERT INTO sms (sender, message, timestamp, received_at)
            VALUES (:sender, :message, :timestamp, :received_at)
        ''',
        **sms,
    )

    post_receive_hook_path = environ.get('SMS2WEB_POST_RECEIVE_HOOK_PATH', None)
    if post_receive_hook_path:
        print('CALLLING HOOK...', json.dumps(sms))
        try:
            print('HOOK OUTPUT:', check_output([post_receive_hook_path, json.dumps(sms)]), file=sys.stderr)
        except CalledProcessError as e:
            print('HOOK ERROR:', e.output, file=sys.stderr)

    return 'THX!'


@app.route('/manifest.json')
def manifest():
    response = Response(render_template("manifest.json"))
    response.headers['Content-Type'] = 'application/json'
    return response


if __name__ =='__main__':
    app.run(host='0.0.0.0', port='4000')
