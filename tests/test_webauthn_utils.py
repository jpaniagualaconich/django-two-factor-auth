import json
import unittest

from django.http import response
from .utils import UserMixin
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from webauthn import const
from two_factor import webauthn_utils
from two_factor.forms import WebauthnDeviceForm
from two_factor.models import WebauthnDevice

class WebAuthnUtilsTest(UserMixin,TestCase):
    
    ASSERTION_DIC = {
        
    } 
    def setUp(self):
        user = self.create_user()
        self.login_user(user=user)
        self.RELYING_PARTY = WebauthnDeviceForm._get_relying_party()
        self.ORIGIN = WebauthnDeviceForm._get_origin()
        self.REGISTRATION_DIC = {
            'challenge': webauthn_utils.make_challenge(),
            'rp':{
                'name': self.RELYING_PARTY['name'],
                'id': self.RELYING_PARTY['name'],
            },
            'user':{
                'id': webauthn_utils.make_user_id(user),
                'name': 'bouke@example.com',
                'displayName': "bouke@example.com",
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
            'authenticatorSelection':{'userVerification':'required'},
        }
        # user's webauthn device creation
        webauthn_device = WebauthnDevice.objects.create()
        # Should be able to select Webauthn method
        response = self.client.post(reverse('two_factor:setup'),
                                    data={'setup_view-current_step': 'welcome'})
        self.assertContains(response, 'webauthn')


    def test_make_credentials_options(self):
        user = self.create_user()
        self.login_user(user=user) 
        make_credential_options = webauthn_utils.make_credentials_options(user=user,relying_party=self.RELYING_PARTY)
        self.assertDictEqual(make_credential_options, webauthn_utils.make_credentials_options(user=user,relying_party=self.RELYING_PARTY))
        self.assertEquals(make_credential_options['excludeCredentials'], self.REGISTRATION_DIC['excludeCredentials'])
        self.assertEquals(make_credential_options['user']['name'],self.REGISTRATION_DIC['user']['name'])
    
    def test_make_registration_response(self):
        user = self.create_user()
        self.login_user(user=user)
        token = 'jlvurcgekuiccfcvgdjffjldedjjgugk'
        request = self.client.get(reverse('two_factor:setup'), 
                                data={'setup_view-current_step': 'webauthn'
                                })
        
        response = self.client.post(reverse('two_factor:setup'),
                                    data={'setup_view-current_step': 'webauthn',
                                        'webauthn-token':token})
        
        request = json.loads(self.request.session['webauthn_registration_request'])
        webauthn_registration_response = webauthn_utils.make_registration_response(
            request, response, self.RELYING_PARTY, self.ORIGIN
        )
    
    def test_make_assertion_options(self):
        self.login_user(user=self.user) 
        make_assertion_options = webauthn_utils.make_assertion_options(user=self.user,relying_party=self.RELYING_PARTY)
        self.assertEquals(make_assertion_options, make_assertion_options)

    def test_make_assertion_response(self):
        pass
    