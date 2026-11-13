#!/bin/sh
# Send a signed sms77 webhook to a local sms2web instance.
#
#   SMS77_SIGNING_SECRET=... ./test_webhook.sh ["message text"]
#
# See https://docs.seven.io/en/rest-api/signing
set -eu

URL="${SMS77_WEBHOOK_URL:-http://localhost:4000/sms77}"
: "${SMS77_SIGNING_SECRET:?SMS77_SIGNING_SECRET must be set}"

TEXT="${1:-Hello World}"
BODY=$(printf '{"webhook_event":"sms_mo","webhook_timestamp":"2021-05-04T13:15:12+02:00","data":{"id":800342,"sender":"491702607871","time":%s,"text":"%s","system":"4915735990598"}}' "$(date +%s)" "$TEXT")

TIMESTAMP=$(date +%s)
NONCE=$(openssl rand -hex 16)
BODY_MD5=$(printf '%s' "$BODY" | openssl dgst -md5 | sed 's/^.*= //')

STRING_TO_SIGN=$(printf '%s\n%s\n%s\n%s\n%s' "$TIMESTAMP" "$NONCE" POST "$URL" "$BODY_MD5")
SIGNATURE=$(printf '%s' "$STRING_TO_SIGN" | openssl dgst -sha256 -hmac "$SMS77_SIGNING_SECRET" | sed 's/^.*= //')

curl -sS -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "X-Timestamp: $TIMESTAMP" \
  -H "X-Nonce: $NONCE" \
  -H "X-Signature: $SIGNATURE" \
  --data-binary "$BODY"
echo
