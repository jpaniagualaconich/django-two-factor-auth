import unittest
from unittest.mock import patch
from .utils import UserMixin
from selenium import webdriver

from django import forms
from django.conf import settings
from django.shortcuts import resolve_url
from django.test import TestCase
import json
from django.urls import reverse

#Imports for Webauthn
from webauthn import const
from two_factor import webauthn_utils
from two_factor.models import WebauthnDevice
from two_factor.forms import WebauthnDeviceForm
#from two_factor.views.core import 





class WebauthnDeviceTest(UserMixin,TestCase):
    
    RELYING_PARTY = WebauthnDeviceForm._get_relying_party()
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
    #La funcion setUp es un metodo para controlar los pre-requisitos
    def setUp(self):
        #create new chrome session
        self.driver = webdriver.Chrome()
        self.driver.implicity_wait(30)
        self.driver.maximize_windows()
        
        #navigate to application
        self.driver.get('dev.mypc.test/account/setup')
        
        self.user = self.create_user()
        return super().setUp()
    
    def test_make_credential_options(self): 
        #self.assertEqual(WebauthnDeviceForm._get_relying_party(), self.RELYING_PARTY)
        self.make_credential_options = webauthn_utils.make_credentials_options(user=self.user,relying_party=self.RELYING_PARTY)
        self.assertEquals(self.REGISTRATION_DIC, self.make_credential_options)
        


        #self.registration_request = json.dumps(self.make_credential_options)
        #self.request.session['webauthn_registration_request'] = self.registration_request
    
    def test_make_registration_response(self):
        response = json.loads(self.cleaned_data['token'])
        try:
            request = json.loads(self.request.session['webauthn_registration_request'])
            webauthn_registration_response = webauthn_utils.make_registration_response(
                request, response, self._get_relying_party(), self._get_origin()
            )

            credentials = webauthn_registration_response.verify()
            key_format = webauthn_utils.get_response_key_format(response)

            self.webauthn_device_info = dict(
                keyHandle=credentials.credential_id.decode('utf-8'),
                publicKey=credentials.public_key.decode('utf-8'),
                signCount=credentials.sign_count,
                format=key_format,
            )

        except Exception as e:
            message = e.args[0] if e.args else _('an unknown error happened.')
            raise forms.ValidationError(_('Token validation failed: %s') % (message, ))

    def tearDown(self):
        #close the browser
        self.driver.quit()
        return super().tearDown()
    