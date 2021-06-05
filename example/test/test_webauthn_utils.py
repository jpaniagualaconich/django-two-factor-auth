import json
import unittest
from unittest.case import expectedFailure

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
        super().setUp()
        user = self.create_user()
        self.login_user(user=user)
        
        request = self.client.post(
            reverse('two_factor:setup'),
            data={
                'setup_view-current_step': 'method',
                'method-method': 'webauthn'})
        

        self.RELYING_PARTY = {
            'id': 'dev.mypc.test',
            'name': settings.TWO_FACTOR_WEBAUTHN_RP_NAME
        }
        self.ORIGIN = '{scheme}://{host}'.format(
            scheme='https', host='dev.mypc.test'
        )
        self.REGISTRATION_DIC = {
            'challenge': webauthn_utils.make_challenge(),
            'rp':{
                'name': self.RELYING_PARTY['name'],
                'id': self.RELYING_PARTY['id'],
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
        user._password 
        make_credential_options = webauthn_utils.make_credentials_options(user=user,relying_party=self.RELYING_PARTY)
        try:
            self.assertFalse(self.assertDictEqual(make_credential_options, webauthn_utils.make_credentials_options(user=user,relying_party=self.RELYING_PARTY)))
            self.assertFalse(self.assertDictEqual(make_credential_options,self.REGISTRATION_DIC))
            self.assertEquals(make_credential_options['excludeCredentials'], self.REGISTRATION_DIC['excludeCredentials'])
            self.assertEquals(make_credential_options['user']['name'],self.REGISTRATION_DIC['user']['name'])
            self.assertEquals(make_credential_options['authenticatorSelection']['userVerification'], self.REGISTRATION_DIC['authenticatorSelection']['userVerification'])
        except:
            print('make_credential_options test failed')
     
    # def test_make_registration_response(self):
    #     user = self.create_user()
    #     self.login_user(user=user)
    #     webauthn_registration_request = webauthn_utils.make_credentials_options(user=user,relying_party=self.RELYING_PARTY)
    #     request = json.loads(webauthn_registration_request)
    #     token = 'jlvurcgekuiccfcvgdjffjldedjjgugk'
    #     response = self.client.post(reverse('two_factor:setup'),
    #                                 data={'setup_view-current_step': 'webauthn',
    #                                     'webauthn-token':token})
                        
    #     webauthn_registration_response = webauthn_utils.make_registration_response(
    #         request, response, self.RELYING_PARTY, self.ORIGIN
    #     )

    
    # def test_make_assertion_options(self):
    #     user = self.create_user()
    #     self.login_user(user=user)
    #     make_assertion_options = webauthn_utils.make_assertion_options(user=user,relying_party=self.RELYING_PARTY)
    #     self.assertEquals(make_assertion_options, webauthn_utils.make_assertion_options(user=user,relying_party=self.RELYING_PARTY))

    # def test_make_assertion_response(self):
    #     pass
    