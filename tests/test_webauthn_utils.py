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

# This constants represents algorithm for pubKeyCredParams
COSE_ALG_ES256 = -7
COSE_ALG_RS256 = -37
COSE_ALG_PS256 = -257


class WebAuthnUtilsTest(UserMixin,TestCase): 
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.login_user(user=self.user)

        self.RELYING_PARTY = {
            'id': 'dev.mypc.test',
            'name': settings.TWO_FACTOR_WEBAUTHN_RP_NAME
        }
        self.ORIGIN = '{scheme}://{host}'.format(
            scheme='https', host='dev.mypc.test'
        )
        self.REGISTRATION_DIC = {
            'challenge': '_webauthn_b64_encode_output',
            'rp':{
                'name': self.RELYING_PARTY['name'],
                'id': self.RELYING_PARTY['id'],
            },
            'user':{
                'id': '_webauthn_b64_encode_output',
                'name': "bouke@example.com",
                'displayName': '',
                'icon': None,
            },
            'pubKeyCredParams': [{
                'alg': COSE_ALG_ES256,
                'type': 'public-key',
            }, {
                'alg': COSE_ALG_RS256,
                'type': 'public-key',
            }, {
                'alg': COSE_ALG_PS256,
                'type': 'public-key',
            }],
            'timeout': 60000,
            'excludeCredentials': [d.as_credential() for d in WebauthnDevice.objects.filter(user=user)[:settings.MAX_EXCLUDED_CREDENTIALS]],
            'attestation': 'direct',
            'extensions':{
                'webauthn.loc': True
            },
            'authenticatorSelection':{
                'userVerification':'required' if settings.TWO_FACTOR_WEBAUTHN_UV_REQUIRED else 'discouraged'
                },
            
            }

    def test_make_credentials_options(self):
        _webauthn_b64_encode_return_value = '_webauthn_b64_encode_output'.encode('utf-8')
        with mock.patch(
            'two_factor.webauthn_utils._webauthn_b64_encode', return_value=_webauthn_b64_encode_return_value
        ) as _webauthn_b64_encode:
            output = webauthn_utils.make_credentials_options(user=self.user,relying_party=self.RELYING_PARTY)
        
        assert _webauthn_b64_encode.called
        assert output == self.REGISTRATION_DIC

    