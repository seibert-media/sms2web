SMS2WEB
=======

It shows sms!

Develop
-------

```bash
export OAUTH2_BASE_URI=http://localhost:5000
export OAUTH2_CLIENT_ID=
export OAUTH2_CLIENT_SECRET=
export OAUTH2_HOSTED_DOMAIN=seibert-media.net
export HELP_URL="help.example.com"
export NUMBERS='+49 123 456 789'
export FLASK_ENV=development
export FLASK_DEBUG=True
export OAUTHLIB_INSECURE_TRANSPORT=1
python3 sms2web/__init__.py
```

Simulate sms77 callback:

(On macos use gpaste from `brew install coreutils`)

```bash
shuf -er -n$(( $RANDOM % 160 ))  {A..Z} {a..z} {0..9} ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' | paste -s -d'' | read TEXT && curl -X POST http://localhost:4000/sms77 --data '{"webhook_event":"sms_mo","webhook_timestamp":"2021-05-04T13:15:12+02:00","data":{"id":800342,"sender":"491702607871","time":'$(date +%s)',"text":"'"$TEXT"'","system":"4915735990598"}}' -H "Content-Type: application/json"
```
