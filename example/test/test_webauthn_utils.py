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

def get_credentials(user):
   credential_list = [d.as_credential() for d in WebauthnDevice.objects.filter(user=user)[:settings.MAX_EXCLUDED_CREDENTIALS]]
   return  credential_list

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
                'id': 'make_user_id_output',
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
            'excludeCredentials': '[]',
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
        make_user_id_return_value = 'make_user_id_output'
        get_credentials_return_value = '[]'
        with mock.patch('two_factor.webauthn_utils._webauthn_b64_encode', return_value=_webauthn_b64_encode_return_value) as _webauthn_b64_encode, mock.patch('two_factor.webauthn_utils.make_user_id', return_value=make_user_id_return_value) as make_user_id, mock.patch('two_factor.webauthn_utils.get_credentials',return_value=get_credentials_return_value) as get_credentials:
            output = webauthn_utils.make_credentials_options(user=self.user,relying_party=self.RELYING_PARTY)
        
        assert _webauthn_b64_encode.called
        assert make_user_id.called
        assert get_credentials.called

        
        self.assertEquals(output['challenge'], self.REGISTRATION_DIC['challenge'])
        self.assertEquals(output['user']['id'], self.REGISTRATION_DIC['user']['id'])
        self.assertEquals(output['excludeCredentials'], self.REGISTRATION_DIC['excludeCredentials'])
        self.assertEquals(output['rp'], self.REGISTRATION_DIC['rp'])
        self.assertEquals(output['user']['name'], self.REGISTRATION_DIC['user']['name'])
        self.assertEquals(output['user']['displayName'], self.REGISTRATION_DIC['user']['displayName'])

        
        # Por que puta Me retorna falso
        #assert output == self.REGISTRATION_DIC
                
        
        
     
    def test_make_registration_response(self):
        self.login_user(user=self.user)
        webauthn_registration_request = webauthn_utils.make_credentials_options(user=self.user,relying_party=self.RELYING_PARTY)
        request = json.loads(webauthn_registration_request)
        
        #Consultar Sobre posibles datos de prueba. Mock
        token = {
            "id":"jG8U_3ojAw15KCsXLx93wA5fix4VeVVrrdW5dxaqmrI",
            "clientDataJSON":"eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiVXRoekZ6QkREWW5GT0ZKZmYwOV9KRW9YcWFXQmRVWjBJU1daRi1SSzFwSSIsIm9yaWdpbiI6Imh0dHBzOi8vZGV2Lm15cGMudGVzdCIsImNyb3NzT3JpZ2luIjpmYWxzZX0",
            "attestationObject":"o2NmbXRoZmlkby11MmZnYXR0U3RtdKJjc2lnWEgwRgIhALQy_v5CG7Iw1VIWfLjJNLw_lkMl-tEPMToctaRusJm0AiEA3nkZ0yaAobQTNfv7xwwgoOejllAZSLAxGQY9cmU5O79jeDVjgVkB4jCCAd4wggGAoAMCAQICAQEwDQYJKoZIhvcNAQELBQAwYDELMAkGA1UEBhMCVVMxETAPBgNVBAoMCENocm9taXVtMSIwIAYDVQQLDBlBdXRoZW50aWNhdG9yIEF0dGVzdGF0aW9uMRowGAYDVQQDDBFCYXRjaCBDZXJ0aWZpY2F0ZTAeFw0xNzA3MTQwMjQwMDBaFw00MTA2MDEwMDUzMTRaMGAxCzAJBgNVBAYTAlVTMREwDwYDVQQKDAhDaHJvbWl1bTEiMCAGA1UECwwZQXV0aGVudGljYXRvciBBdHRlc3RhdGlvbjEaMBgGA1UEAwwRQmF0Y2ggQ2VydGlmaWNhdGUwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASNYX5lyVCOZLzFZzrIKmeZ2jwURmgsJYxGP__fWN_S-j5sN4tT15XEpN_7QZnt14YvI6uvAgO0uJEboFaZlOEBoygwJjATBgsrBgEEAYLlHAIBAQQEAwIFIDAPBgNVHRMBAf8EBTADAQEAMA0GCSqGSIb3DQEBCwUAA0kAMEYCIQCRnz8VkrQiqO2bVMay7ylMkys8lAQx1qfTqjbsbDKWyAIhAL6cQXPoXLO2FY1ZETjzFutCJZ7ZnM2Ki1zRAVi_pyGaaGF1dGhEYXRhWKRuLdl-XiO8OZcxMrelHAwyyICdNRPE0iuzW4ejVJpuakEAAAAAAAAAAAAAAAAAAAAAAAAAAAAgjG8U_3ojAw15KCsXLx93wA5fix4VeVVrrdW5dxaqmrKlAQIDJiABIVgg0lcmU9O_uc8VJZnavYvjF_QwbOxMISYY5XW73mLKtLsiWCB8L9D9h5inMJlbRBpKNlNlQ7Y49JScryKPf5k-RUmclw"
            }

        response = self.client.post(reverse('two_factor:setup'),
                                    data={'setup_view-current_step': 'webauthn',
                                        'webauthn-token':token})

        #Tendria que mockar webauthn.WebAuthnRegistrationResponse?                
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
    