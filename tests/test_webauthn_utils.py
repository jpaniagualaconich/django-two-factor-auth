import json
import unittest
from .utils import UserMixin
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from webauthn import const
from two_factor import webauthn_utils
from two_factor.forms import WebauthnDeviceForm

class WebAuthnUtilsTest(UserMixin,TestCase):
    REGISTRATION_DIC = {
        'challenge': webauthn_utils.make_challenge(),
        'rp':{
            'name': RELYING_PARTY['name'],
            'id': RELYING_PARTY['name'],
        },
        'user':{
            'id': webauthn_utils.make_user_id(),
            'name': 'testuser',
            'displayName': "A test User",
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
        'timeout': None,
        'excludeCredentials': [],
        'attestation': None,
        'extensions':{
            'webauthn.loc': True
        }
    } 
    def setUp(self):
        self.user = self.create_user()
        self.RELYING_PARTY = WebauthnDeviceForm._get_relying_party()
        self.ORIGIN = WebauthnDeviceForm._get_origin()

    def test_make_credential_options(self):
        self.login_user(user=self.user) 
        make_credential_options = webauthn_utils.make_credentials_options(user=self.user,relying_party=self.RELYING_PARTY)
        self.assertEquals(make_credential_options, make_credential_options)
    
    def test_make_registration_response(self):
        #Estos debo modificar de alguna forma
        response = json.loads(self.cleaned_data['token'])
        request = json.loads(self.request.session['webauthn_registration_request'])
        webauthn_registration_response = webauthn_utils.make_registration_response(
            request, response, self.RELYING_PARTY, self.ORIGIN
        )
    
    def test_make_assertion_options(self):
        pass

    def test_make_assertion_response(self):
        pass
    