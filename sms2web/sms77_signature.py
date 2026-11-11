"""Verification of signed webhooks sent by sms77/seven.io.

See https://docs.seven.io/en/rest-api/signing and
https://docs.seven.io/en/rest-api/webhooks#security
"""

from hashlib import md5
from hmac import compare_digest, new as new_hmac
from os import environ
from sqlite3 import IntegrityError
from time import time

from lib import delete, insert

# Webhooks must not be older/newer than this many seconds.
WINDOW_SECONDS = 30

# A nonce has to be unique for every delivery attempt. Keep it around a bit
# longer than the timestamp window so that a replay cannot slip through just
# because the original request is about to leave the window.
NONCE_TTL_SECONDS = 60


def target_url(request):
    """The complete URL the webhook was sent to.

    Behind a reverse proxy `request.url` can differ from the URL seven.io
    signed, so it can be overridden explicitly.
    """
    return environ.get('SMS77_WEBHOOK_URL') or request.url


def content_md5(body):
    return md5(body).hexdigest()


def string_to_sign(timestamp, nonce, method, url, body_md5, account_id=None):
    lines = [str(timestamp), nonce, method, url, body_md5]
    if account_id:
        lines.append(account_id)
    return '\n'.join(lines)


def _consume_nonce(nonce, now):
    """Remember a nonce, return False if it has been used before.

    Stored in the database so that replay protection also works when the app
    runs in more than one process.
    """
    delete('DELETE FROM sms77_nonce WHERE expires <= :now', now=now)

    try:
        insert(
            '''
                INSERT INTO sms77_nonce (nonce, expires)
                VALUES (:nonce, :expires)
            ''',
            nonce=nonce,
            expires=now + NONCE_TTL_SECONDS,
        )
    except IntegrityError:
        return False

    return True


def verify(request):
    """Validate the signature of an incoming webhook.

    Returns a (ok, reason) tuple. `reason` is meant for logging only.
    """
    secret = environ.get('SMS77_SIGNING_SECRET')
    if not secret:
        return False, 'SMS77_SIGNING_SECRET is not configured'

    signature = request.headers.get('X-Signature')
    timestamp = request.headers.get('X-Timestamp')
    nonce = request.headers.get('X-Nonce')
    if not signature or not timestamp or not nonce:
        return False, 'missing X-Signature, X-Timestamp or X-Nonce header'

    try:
        timestamp = int(timestamp)
    except ValueError:
        return False, 'X-Timestamp is not an integer'

    now = int(time())
    if abs(now - timestamp) > WINDOW_SECONDS:
        return False, f'X-Timestamp outside of the {WINDOW_SECONDS}s window'

    expected = new_hmac(
        secret.encode(),
        string_to_sign(
            timestamp,
            nonce,
            request.method,
            target_url(request),
            content_md5(request.get_data(cache=True)),
            request.headers.get('X-Account-Id'),
        ).encode(),
        'sha256',
    ).hexdigest()

    if not compare_digest(expected, signature.strip().lower()):
        return False, 'X-Signature does not match'

    # Only authenticated requests may populate the nonce cache, otherwise
    # anyone could grow it with garbage nonces.
    if not _consume_nonce(nonce, now):
        return False, 'X-Nonce has already been used'

    return True, 'ok'
