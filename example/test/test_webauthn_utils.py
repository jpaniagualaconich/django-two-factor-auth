import json
import unittest
from unittest.case import expectedFailure

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
    ASSERTION_DIC = {
        
    } 
    def setUp(self):
        super().setUp()
        self.user = self.create_user()
        self.login_user(user=self.user)
        
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
                'id': webauthn_utils.make_user_id(self.user),
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
            'excludeCredentials': [d.as_credential() for d in WebauthnDevice.objects.filter(user=self.user)[:settings.MAX_EXCLUDED_CREDENTIALS]],
            'attestation': 'direct',
            'extensions':{
                'webauthn.loc': True
            },
            'authenticatorSelection':{
                'userVerification':'required' if settings.TWO_FACTOR_WEBAUTHN_UV_REQUIRED else 'discouraged'
                },
        }


    def test_make_credentials_options(self):
        self.login_user(user=self.user)
        make_credential_options = webauthn_utils.make_credentials_options(user=self.user,relying_party=self.RELYING_PARTY)
        
        # Assertions for make_credentials_options
        self.assertEquals(make_credential_options['excludeCredentials'], self.REGISTRATION_DIC['excludeCredentials'])
        self.assertEquals(make_credential_options['user']['name'],self.REGISTRATION_DIC['user']['name'])
        self.assertEquals(make_credential_options['authenticatorSelection']['userVerification'], self.REGISTRATION_DIC['authenticatorSelection']['userVerification'])
        self.assertFalse(make_credential_options['challenge'] == self.REGISTRATION_DIC['challenge'])
        self.assertEquals(make_credential_options['user']['id'],self.REGISTRATION_DIC['user']['id'])
        
        
        
     
    def test_make_registration_response(self):
        self.login_user(user=self.user)
        webauthn_registration_request = webauthn_utils.make_credentials_options(user=self.user,relying_party=self.RELYING_PARTY)
        request = json.loads(webauthn_registration_request)
        
        #Consultar Sobre posibles datos de prueba
        token = {
            "id":"jG8U_3ojAw15KCsXLx93wA5fix4VeVVrrdW5dxaqmrI",
            "clientDataJSON":"eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiVXRoekZ6QkREWW5GT0ZKZmYwOV9KRW9YcWFXQmRVWjBJU1daRi1SSzFwSSIsIm9yaWdpbiI6Imh0dHBzOi8vZGV2Lm15cGMudGVzdCIsImNyb3NzT3JpZ2luIjpmYWxzZX0",
            "attestationObject":"o2NmbXRoZmlkby11MmZnYXR0U3RtdKJjc2lnWEgwRgIhALQy_v5CG7Iw1VIWfLjJNLw_lkMl-tEPMToctaRusJm0AiEA3nkZ0yaAobQTNfv7xwwgoOejllAZSLAxGQY9cmU5O79jeDVjgVkB4jCCAd4wggGAoAMCAQICAQEwDQYJKoZIhvcNAQELBQAwYDELMAkGA1UEBhMCVVMxETAPBgNVBAoMCENocm9taXVtMSIwIAYDVQQLDBlBdXRoZW50aWNhdG9yIEF0dGVzdGF0aW9uMRowGAYDVQQDDBFCYXRjaCBDZXJ0aWZpY2F0ZTAeFw0xNzA3MTQwMjQwMDBaFw00MTA2MDEwMDUzMTRaMGAxCzAJBgNVBAYTAlVTMREwDwYDVQQKDAhDaHJvbWl1bTEiMCAGA1UECwwZQXV0aGVudGljYXRvciBBdHRlc3RhdGlvbjEaMBgGA1UEAwwRQmF0Y2ggQ2VydGlmaWNhdGUwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASNYX5lyVCOZLzFZzrIKmeZ2jwURmgsJYxGP__fWN_S-j5sN4tT15XEpN_7QZnt14YvI6uvAgO0uJEboFaZlOEBoygwJjATBgsrBgEEAYLlHAIBAQQEAwIFIDAPBgNVHRMBAf8EBTADAQEAMA0GCSqGSIb3DQEBCwUAA0kAMEYCIQCRnz8VkrQiqO2bVMay7ylMkys8lAQx1qfTqjbsbDKWyAIhAL6cQXPoXLO2FY1ZETjzFutCJZ7ZnM2Ki1zRAVi_pyGaaGF1dGhEYXRhWKRuLdl-XiO8OZcxMrelHAwyyICdNRPE0iuzW4ejVJpuakEAAAAAAAAAAAAAAAAAAAAAAAAAAAAgjG8U_3ojAw15KCsXLx93wA5fix4VeVVrrdW5dxaqmrKlAQIDJiABIVgg0lcmU9O_uc8VJZnavYvjF_QwbOxMISYY5XW73mLKtLsiWCB8L9D9h5inMJlbRBpKNlNlQ7Y49JScryKPf5k-RUmclw"
            }

        response = self.client.post(reverse('two_factor:setup'),
                                    data={'setup_view-current_step': 'webauthn',
                                        'webauthn-token':token})
                        
        webauthn_registration_response = webauthn_utils.make_registration_response(
            request, response, self.RELYING_PARTY, self.ORIGIN
        )

    
    # def test_make_assertion_options(self):
    #     user = self.create_user()
    #     self.login_user(user=user)
    #     make_assertion_options = webauthn_utils.make_assertion_options(user=user,relying_party=self.RELYING_PARTY)
    #     self.assertEquals(make_assertion_options, webauthn_utils.make_assertion_options(user=user,relying_party=self.RELYING_PARTY))

    # def test_make_assertion_response(self):
    #     pass
    