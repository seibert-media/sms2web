import json
import os
import secrets
import sys
import tempfile
import unittest
from hashlib import md5
from hmac import new as new_hmac
from time import time
from unittest.mock import patch

# The app reads its configuration at import time.
os.environ.setdefault('DATA_PATH', tempfile.mkdtemp(prefix='sms2web-test-'))
os.environ.setdefault('OAUTH2_ALLOWED_DOMAINS', 'example.com')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from sms2web import app  # noqa: E402

# The app imports its helpers as top-level modules, so use the very same
# instances here instead of importing them a second time.
lib = sys.modules['lib']

SECRET = 'test-signing-secret'
URL = 'http://localhost/sms77'

PAYLOAD = {
    'webhook_event': 'sms_mo',
    'webhook_timestamp': '2021-05-04T13:15:12+02:00',
    'data': {
        'id': 800342,
        'sender': '491702607871',
        'time': 1620126912,
        'text': 'Test',
        'system': '4915735990598',
    },
}


def signed_headers(body, timestamp=None, nonce=None,
                   secret=SECRET, url=URL):
    timestamp = int(time()) if timestamp is None else timestamp
    nonce = secrets.token_hex(16) if nonce is None else nonce
    body_md5 = md5(body).hexdigest()
    string_to_sign = '\n'.join(
        [str(timestamp), nonce, 'POST', url, body_md5]
    )
    signature = new_hmac(secret.encode(), string_to_sign.encode(), 'sha256').hexdigest()
    return {
        'Content-Type': 'application/json',
        'X-Timestamp': str(timestamp),
        'X-Nonce': nonce,
        'X-Signature': signature,
    }


class SignatureTest(unittest.TestCase):
    def setUp(self):
        lib.delete('DELETE FROM sms77_nonce')
        self.client = app.test_client()
        self.body = json.dumps(PAYLOAD).encode()
        self.env = patch.dict(os.environ, {
            'SMS77_SIGNING_SECRET': SECRET,
            'SMS77_WEBHOOK_URL': URL,
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    def post(self, headers, body=None):
        return self.client.post(
            '/sms77',
            data=self.body if body is None else body,
            headers=headers,
        )

    def test_valid_signature_is_accepted(self):
        response = self.post(signed_headers(self.body))
        self.assertEqual(200, response.status_code)

    def test_tampered_body_is_rejected(self):
        headers = signed_headers(self.body)
        response = self.post(headers, body=self.body.replace(b'Test', b'Evil'))
        self.assertEqual(403, response.status_code)

    def test_stale_timestamp_is_rejected(self):
        response = self.post(signed_headers(self.body, timestamp=int(time()) - 31))
        self.assertEqual(403, response.status_code)

    def test_replayed_nonce_is_rejected(self):
        nonce = secrets.token_hex(16)
        headers = signed_headers(self.body, nonce=nonce)
        self.assertEqual(200, self.post(headers).status_code)
        self.assertEqual(403, self.post(headers).status_code)

    def test_expired_nonce_is_forgotten(self):
        nonce = secrets.token_hex(16)
        lib.insert(
            '''
                INSERT INTO sms77_nonce (nonce, expires)
                VALUES (:nonce, :expires)
            ''',
            nonce=nonce,
            expires=int(time()) - 1,
        )
        headers = signed_headers(self.body, nonce=nonce)
        self.assertEqual(200, self.post(headers).status_code)

    def test_missing_headers_are_rejected(self):
        headers = signed_headers(self.body)
        del headers['X-Signature']
        self.assertEqual(403, self.post(headers).status_code)

    def test_wrong_secret_is_rejected(self):
        headers = signed_headers(self.body, secret='not-the-secret')
        self.assertEqual(403, self.post(headers).status_code)

    def test_malformed_payload_is_rejected(self):
        body = b'{"webhook_event": "sms_mo"}'
        response = self.post(signed_headers(body), body=body)
        self.assertEqual(400, response.status_code)

    def test_unconfigured_secret_is_rejected(self):
        with patch.dict(os.environ, {'SMS77_SIGNING_SECRET': ''}):
            response = self.post(signed_headers(self.body))
        self.assertEqual(503, response.status_code)


if __name__ == '__main__':
    unittest.main()
