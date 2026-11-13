SMS2WEB
=======

It shows sms!

Develop
-------

```bash
export OAUTH2_BASE_URI=http://localhost:4000
export OAUTH2_CLIENT_ID=
export OAUTH2_CLIENT_SECRET=
export OAUTH2_HOSTED_DOMAIN=seibert-media.net
export OAUTH2_ALLOWED_DOMAINS=seibert-media.net,foo.com
export ALLOWLIST_URL="https://my.wiki/sms2web/restricted_to"
export HELP_URL="help.example.com"
export NUMBERS='+49 123 456 789'
export SMS77_SIGNING_SECRET='your-seven.io-signing-key'
export SMS77_WEBHOOK_URL='http://localhost:4000/sms77'
export FLASK_DEBUG=True
export OAUTHLIB_INSECURE_TRANSPORT=1
export SMS2WEB_POST_RECEIVE_HOOK_PATH="./test_hook.sh"
python3 sms2web/__init__.py
```

Webhook signature
-----------------

`POST /sms77` only accepts requests signed by sms77/seven.io, see
<https://docs.seven.io/en/rest-api/signing>. Set `SMS77_SIGNING_SECRET` to the
signing key of your account (Dashboard → Developer → API settings). Without it
every webhook is rejected with `503`; requests with a missing or invalid
signature, a timestamp outside of the 30 second window or a replayed nonce are
rejected with `403`.

`SMS77_WEBHOOK_URL` must be the complete URL seven.io sends the webhook to. It
defaults to the URL Flask sees, which is wrong behind a TLS terminating proxy,
so set it explicitly in production.

Simulate sms77 callback:

```bash
SMS77_SIGNING_SECRET='your-seven.io-signing-key' ./test_webhook.sh "Hello World"
```
