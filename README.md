SMS2WEB
=======

It shows sms!

Develop
-------

```bash
export OAUTH2_BASE_URI=http://localhost:5000
export OAUTH2_CLIENT_ID=49012788941-rcbn217mav73ssgstma94j0gflcc13ku.apps.googleusercontent.com
export OAUTH2_CLIENT_SECRET= # https://console.developers.google.com/apis/credentials/oauthclient/49012788941-rcbn217mav73ssgstma94j0gflcc13ku.apps.googleusercontent.com?project=49012788941
export OAUTH2_HOSTED_DOMAIN=seibert-media.net
export HELP_URL="https://confluence.apps.seibert-media.net/x/GkLODQ"
export NUMBERS='+49 123 456 789'
export FLASK_ENV=development
export FLASK_DEBUG=True
export OAUTHLIB_INSECURE_TRANSPORT=1
python3 sms2web/__init__.py
```

Simulate sms77 callback:

```bash
shuf -er -n$(( $RANDOM % 160 ))  {A..Z} {a..z} {0..9} ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' ' | paste -sd "" | read TEXT && curl -X POST http://localhost:5000/sms77 --data '{"webhook_event":"sms_mo","webhook_timestamp":"2021-05-04T13:15:12+02:00","data":{"id":800342,"sender":"491702607871","time":'$(date +%s)',"text":"'"$TEXT"'","system":"4915735990598"}}' -H "Content-Type: application/json"
```
