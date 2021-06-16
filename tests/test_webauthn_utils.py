import json
import unittest
from unittest.case import expectedFailure
from unittest import mock

from django.http import response
from .utils import UserMixin
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

# Webauthn imports
from two_factor import webauthn_utils
from two_factor.forms import WebauthnDeviceForm
from two_factor.models import WebauthnDevice

from webauthn.webauthn import COSE_ALG_ES256, COSE_ALG_PS256, COSE_ALG_RS256


class WebAuthnUtilsTest(UserMixin,TestCase): 
    def setUp(self):
        super().setUp()
        self.user = self.create_user()

    def test_get_credentials(self):
        user_webauthn_devices = [
            WebauthnDevice(
                user=self.user,
                public_key=f'public-key-{pk}',
                key_handle=f'key-handle-{pk}',
                sign_count=0,
            ) for pk in range(3)
        ]
        max_excluded_credentials = len(user_webauthn_devices) - 1
        webauthn_device_objects=mock.Mock(
            filter=mock.Mock(return_value=user_webauthn_devices),
        )

        with mock.patch(
            'two_factor.webauthn_utils.WebauthnDevice.objects',
            new_callable=mock.PropertyMock,
            return_value=webauthn_device_objects,
        ), self.settings(MAX_EXCLUDED_CREDENTIALS=max_excluded_credentials):
            credentials = webauthn_utils.get_credentials(self.user)

        assert credentials == [
            {'id': 'key-handle-0', 'type': 'public-key'},
            {'id': 'key-handle-1', 'type': 'public-key'},
        ]

    def test_make_credential_options(self):
        encoded_urandom = 'a-b64-encoded-random-number'.encode('utf-8')
        encoded_hashed_id = 'a-b64-encoded-hashed-id'.encode('utf-8')
        credentials = 'a-list-of-credentials'
        relying_party = {'id': 'rp-id', 'name': 'rp-name'}

        with mock.patch(
            'two_factor.webauthn_utils._webauthn_b64_encode',
            side_effect=[encoded_urandom, encoded_hashed_id],
        ) as _webauthn_b64_encode, mock.patch(
            'two_factor.webauthn_utils.get_credentials',
            return_value=credentials,
        ) as get_credentials:
            output = webauthn_utils.make_credential_options(
                user=self.user, relying_party=relying_party)
        
        assert _webauthn_b64_encode.call_count == 2
        assert get_credentials.called

        pub_key_cred_params = output.pop('pubKeyCredParams')
        assert sorted(pub_key_cred_params, key=lambda x: x['alg']) == sorted([
            {'alg': COSE_ALG_ES256, 'type': 'public-key'},
            {'alg': COSE_ALG_RS256, 'type': 'public-key'},
            {'alg': COSE_ALG_PS256, 'type': 'public-key'},
        ], key=lambda x: x['alg'])

        assert output == {
            'challenge': 'a-b64-encoded-random-number',
            'rp': relying_party,
            'user': {'id': 'a-b64-encoded-hashed-id', 'name': self.user.email, 'displayName': ''},
            'timeout': 60000,
            'excludeCredentials': credentials,
            'attestation': 'direct',
            'extensions': {'webauthn.loc': True},
            'authenticatorSelection': {'userVerification': 'discouraged'},
        }
