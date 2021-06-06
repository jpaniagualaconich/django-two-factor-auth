#En este archivo vamos a hacer los integration test
import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .utils import UserMixin


class LoginTest(UserMixin, TestCase):
    def _post(self, data=None):
        return self.client.post(reverse('two_factor:login'), data=data)
    
    @classmethod
    def setUp(self):
        # Create a new Chrome session
        self.webdriver = webdriver.Chrome(ChromeDriverManager().install())
        self.webdriver.implicitly_wait(30)
        self.webdriver.maximize_window()
        
        # Navigate into aplication
        self.webdriver.get("https://dev.mypc.test/")

    @classmethod    
    def tearDown(self):
        self.webdriver.quit()


    def test_valid_login(self):
        # Navigate into aplication login page
        login_url = "https://dev.mypc.test/account/login/"
        self.webdriver.get(login_url)
        self.assertEquals(login_url,self.webdriver.current_url)

        # Completed Form
        username = self.webdriver.find_element_by_id('id_auth-username')
        username.clear()
        username.send_keys("user5")

        password = self.webdriver.find_element_by_id('id_auth-password')
        password.clear()
        password.send_keys("user5")

        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Navegate into aplication two_factor's device register
        redirect_url = 'https://dev.mypc.test/account/two_factor/'
        current_url = self.webdriver.current_url
        self.assertEquals(current_url,redirect_url)
        
        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//a[@class='btn btn-primary']")
        button_next.click()

        # Confirm the creation of the second factor device
        redirect_url = 'https://dev.mypc.test/account/two_factor/setup/'
        current_url = self.webdriver.current_url
        self.assertEquals(current_url,redirect_url)
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Select wizard -> webauthn
        redirect_url = 'https://dev.mypc.test/account/two_factor/setup/'
        current_url = self.webdriver.current_url
        self.assertEquals(current_url,redirect_url)
        webauthn_input = self.webdriver.find_element_by_xpath("//input[@value='webauthn']")
        webauthn_input.click()
        button_next = self.webdriver.find_element_by_xpath("//button[@class='btn btn-primary']")
        button_next.click()
        
        # Wait for authenticator(webauthn)
        try:
            token_present = EC.presence_of_element_located((By.XPATH, "//input[@name='webauthn-token']"))
            WebDriverWait(webdriver,TimeoutError).until(token_present)
        except:
            print("no anda")
        self.webdriver.find_element_by_xpath("//a[@class='float-right btn btn-link']")
        
        # Confirmation
        redirect_url = 'https://dev.mypc.test/account/two_factor/'
        current_url = self.webdriver.current_url
        self.assertEquals(current_url,redirect_url)






    # def test_valid_login_with_custom_post_redirect(self):
    #     redirect_url = reverse('two_factor:setup')
    #     self.create_user()
    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth',
    #                            'next': redirect_url})
    #     self.assertRedirects(response, redirect_url)

    # def test_valid_login_with_redirect_field_name(self):
    #     redirect_url = reverse('two_factor:setup')
    #     self.create_user()
    #     response = self.client.post(
    #         '%s?%s' % (reverse('custom-field-name-login'), 'next_page=' + redirect_url),
    #         {'auth-username': 'bouke@example.com',
    #          'auth-password': 'secret',
    #          'login_view-current_step': 'auth'})
    #     self.assertRedirects(response, redirect_url)

    # def test_valid_login_with_allowed_external_redirect(self):
    #     redirect_url = 'https://test.allowed-success-url.com'
    #     self.create_user()
    #     response = self.client.post(
    #         '%s?%s' % (reverse('custom-allowed-success-url-login'), 'next=' + redirect_url),
    #         {'auth-username': 'bouke@example.com',
    #          'auth-password': 'secret',
    #          'login_view-current_step': 'auth'})
    #     self.assertRedirects(response, redirect_url, fetch_redirect_response=False)

    # def test_valid_login_with_disallowed_external_redirect(self):
    #     redirect_url = 'https://test.disallowed-success-url.com'
    #     self.create_user()
    #     response = self.client.post(
    #         '%s?%s' % (reverse('custom-allowed-success-url-login'), 'next=' + redirect_url),
    #         {'auth-username': 'bouke@example.com',
    #          'auth-password': 'secret',
    #          'login_view-current_step': 'auth'})
    #     self.assertRedirects(response, reverse('two_factor:profile'), fetch_redirect_response=False)

    # @mock.patch('two_factor.views.core.time')
    # def test_valid_login_primary_key_stored(self, mock_time):
    #     mock_time.time.return_value = 12345.12
    #     user = self.create_user()
    #     user.totpdevice_set.create(name='default',
    #                                key=random_hex())

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')

    #     self.assertEqual(self.client.session['wizard_login_view']['user_pk'], str(user.pk))
    #     self.assertEqual(
    #         self.client.session['wizard_login_view']['user_backend'],
    #         'django.contrib.auth.backends.ModelBackend')
    #     self.assertEqual(self.client.session['wizard_login_view']['authentication_time'], 12345)

    # @mock.patch('two_factor.views.core.time')
    # def test_valid_login_post_auth_session_clear_of_form_data(self, mock_time):
    #     mock_time.time.return_value = 12345.12
    #     user = self.create_user()
    #     user.totpdevice_set.create(name='default',
    #                                key=random_hex())

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')

    #     self.assertEqual(self.client.session['wizard_login_view']['user_pk'], str(user.pk))
    #     self.assertEqual(self.client.session['wizard_login_view']['step'], 'token')
    #     self.assertEqual(self.client.session['wizard_login_view']['step_data'], {'auth': None})
    #     self.assertEqual(self.client.session['wizard_login_view']['step_files'], {'auth': {}})
    #     self.assertEqual(self.client.session['wizard_login_view']['validated_step_data'], {})

    # @mock.patch('two_factor.views.core.logger')
    # @mock.patch('two_factor.views.core.time')
    # def test_valid_login_expired(self, mock_time, mock_logger):
    #     mock_time.time.return_value = 12345.12
    #     user = self.create_user()
    #     device = user.totpdevice_set.create(name='default',
    #                                         key=random_hex())

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')

    #     self.assertEqual(self.client.session['wizard_login_view']['user_pk'], str(user.pk))
    #     self.assertEqual(
    #         self.client.session['wizard_login_view']['user_backend'],
    #         'django.contrib.auth.backends.ModelBackend')
    #     self.assertEqual(self.client.session['wizard_login_view']['authentication_time'], 12345)

    #     mock_time.time.return_value = 20345.12

    #     response = self._post({'token-otp_token': totp(device.bin_key),
    #                            'login_view-current_step': 'token'})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotContains(response, 'Token:')
    #     self.assertContains(response, 'Password:')
    #     self.assertContains(response, 'Your session has timed out. Please login again.')

    #     # Check that a message was logged.
    #     mock_logger.info.assert_called_with(
    #         "User's authentication flow has timed out. The user "
    #         "has been redirected to the initial auth form.")

    # @override_settings(TWO_FACTOR_LOGIN_TIMEOUT=0)
    # @mock.patch('two_factor.views.core.time')
    # def test_valid_login_no_timeout(self, mock_time):
    #     mock_time.time.return_value = 12345.12
    #     user = self.create_user()
    #     device = user.totpdevice_set.create(name='default',
    #                                         key=random_hex())

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')

    #     self.assertEqual(self.client.session['wizard_login_view']['user_pk'], str(user.pk))
    #     self.assertEqual(
    #         self.client.session['wizard_login_view']['user_backend'],
    #         'django.contrib.auth.backends.ModelBackend')
    #     self.assertEqual(self.client.session['wizard_login_view']['authentication_time'], 12345)

    #     mock_time.time.return_value = 20345.12

    #     response = self._post({'token-otp_token': totp(device.bin_key),
    #                            'login_view-current_step': 'token'})
    #     self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))
    #     self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))

    # def test_valid_login_with_redirect_authenticated_user(self):
    #     user = self.create_user()
    #     response = self.client.get(
    #         reverse('custom-redirect-authenticated-user-login')
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.client.force_login(user)
    #     response = self.client.get(
    #         reverse('custom-redirect-authenticated-user-login')
    #     )
    #     self.assertRedirects(response, reverse('two_factor:profile'))

    # def test_valid_login_with_redirect_authenticated_user_loop(self):
    #     redirect_url = reverse('custom-redirect-authenticated-user-login')
    #     user = self.create_user()
    #     self.client.force_login(user)
    #     with self.assertRaises(ValueError):
    #         self.client.get(
    #             '%s?%s' % (reverse('custom-redirect-authenticated-user-login'), 'next=' + redirect_url),
    #         )

    # @mock.patch('two_factor.views.core.signals.user_verified.send')
    # def test_with_generator(self, mock_signal):
    #     user = self.create_user()
    #     device = user.totpdevice_set.create(name='default',
    #                                         key=random_hex())

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')
    #     self.assertContains(response, 'autofocus="autofocus"')
    #     self.assertContains(response, 'inputmode="numeric"')
    #     self.assertContains(response, 'autocomplete="one-time-code"')

    #     response = self._post({'token-otp_token': '123456',
    #                            'login_view-current_step': 'token'})
    #     self.assertEqual(response.context_data['wizard']['form'].errors,
    #                      {'__all__': ['Invalid token. Please make sure you '
    #                                   'have entered it correctly.']})

    #     # reset throttle because we're not testing that
    #     device.throttle_reset()

    #     response = self._post({'token-otp_token': totp(device.bin_key),
    #                            'login_view-current_step': 'token'})
    #     self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

    #     self.assertEqual(device.persistent_id,
    #                      self.client.session.get(DEVICE_ID_SESSION_KEY))

    #     # Check that the signal was fired.
    #     mock_signal.assert_called_with(sender=mock.ANY, request=mock.ANY, user=user, device=device)

    # @mock.patch('two_factor.views.core.signals.user_verified.send')
    # def test_throttle_with_generator(self, mock_signal):
    #     user = self.create_user()
    #     device = user.totpdevice_set.create(name='default',
    #                                         key=random_hex())

    #     self._post({'auth-username': 'bouke@example.com',
    #                 'auth-password': 'secret',
    #                 'login_view-current_step': 'auth'})

    #     # throttle device
    #     device.throttle_increment()

    #     response = self._post({'token-otp_token': totp(device.bin_key),
    #                            'login_view-current_step': 'token'})
    #     self.assertEqual(response.context_data['wizard']['form'].errors,
    #                      {'__all__': ['Invalid token. Please make sure you '
    #                                   'have entered it correctly.']})

    # @mock.patch('two_factor.gateways.fake.Fake')
    # @mock.patch('two_factor.views.core.signals.user_verified.send')
    # @override_settings(
    #     TWO_FACTOR_SMS_GATEWAY='two_factor.gateways.fake.Fake',
    #     TWO_FACTOR_CALL_GATEWAY='two_factor.gateways.fake.Fake',
    # )
    # def test_with_backup_phone(self, mock_signal, fake):
    #     user = self.create_user()
    #     for no_digits in (6, 8):
    #         with self.settings(TWO_FACTOR_TOTP_DIGITS=no_digits):
    #             user.totpdevice_set.create(name='default', key=random_hex(),
    #                                        digits=no_digits)
    #             device = user.phonedevice_set.create(name='backup', number='+31101234567',
    #                                                  method='sms',
    #                                                  key=random_hex())

    #             # Backup phones should be listed on the login form
    #             response = self._post({'auth-username': 'bouke@example.com',
    #                                    'auth-password': 'secret',
    #                                    'login_view-current_step': 'auth'})
    #             self.assertContains(response, 'Send text message to +31 ** *** **67')

    #             # Ask for challenge on invalid device
    #             response = self._post({'auth-username': 'bouke@example.com',
    #                                    'auth-password': 'secret',
    #                                    'challenge_device': 'MALICIOUS/INPUT/666'})
    #             self.assertContains(response, 'Send text message to +31 ** *** **67')

    #             # Ask for SMS challenge
    #             response = self._post({'auth-username': 'bouke@example.com',
    #                                    'auth-password': 'secret',
    #                                    'challenge_device': device.persistent_id})
    #             self.assertContains(response, 'We sent you a text message')

    #             test_call_kwargs = fake.return_value.send_sms.call_args[1]
    #             self.assertEqual(test_call_kwargs['device'], device)
    #             self.assertIn(test_call_kwargs['token'],
    #                           [str(totp(device.bin_key, digits=no_digits, drift=i)).zfill(no_digits)
    #                            for i in [-1, 0]])

    #             # Ask for phone challenge
    #             device.method = 'call'
    #             device.save()
    #             response = self._post({'auth-username': 'bouke@example.com',
    #                                    'auth-password': 'secret',
    #                                    'challenge_device': device.persistent_id})
    #             self.assertContains(response, 'We are calling your phone right now')

    #             test_call_kwargs = fake.return_value.make_call.call_args[1]
    #             self.assertEqual(test_call_kwargs['device'], device)
    #             self.assertIn(test_call_kwargs['token'],
    #                           [str(totp(device.bin_key, digits=no_digits, drift=i)).zfill(no_digits)
    #                            for i in [-1, 0]])

    #         # Valid token should be accepted.
    #         response = self._post({'token-otp_token': totp(device.bin_key),
    #                                'login_view-current_step': 'token'})
    #         self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))
    #         self.assertEqual(device.persistent_id,
    #                          self.client.session.get(DEVICE_ID_SESSION_KEY))

    #         # Check that the signal was fired.
    #         mock_signal.assert_called_with(sender=mock.ANY, request=mock.ANY, user=user, device=device)

    # @mock.patch('two_factor.views.core.signals.user_verified.send')
    # def test_with_backup_token(self, mock_signal):
    #     user = self.create_user()
    #     user.totpdevice_set.create(name='default', key=random_hex())
    #     device = user.staticdevice_set.create(name='backup')
    #     device.token_set.create(token='abcdef123')

    #     # Backup phones should be listed on the login form
    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Backup Token')

    #     # Should be able to go to backup tokens step in wizard
    #     response = self._post({'wizard_goto_step': 'backup'})
    #     self.assertContains(response, 'backup tokens')

    #     # Wrong codes should not be accepted
    #     response = self._post({'backup-otp_token': 'WRONG',
    #                            'login_view-current_step': 'backup'})
    #     self.assertEqual(response.context_data['wizard']['form'].errors,
    #                      {'__all__': ['Invalid token. Please make sure you '
    #                                   'have entered it correctly.']})
    #     # static devices are throttled
    #     device.throttle_reset()

    #     # Valid token should be accepted.
    #     response = self._post({'backup-otp_token': 'abcdef123',
    #                            'login_view-current_step': 'backup'})
    #     self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

    #     # Check that the signal was fired.
    #     mock_signal.assert_called_with(sender=mock.ANY, request=mock.ANY, user=user, device=device)

    # @mock.patch('two_factor.views.utils.logger')
    # def test_reset_wizard_state(self, mock_logger):
    #     self.create_user()
    #     self.enable_otp()

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')

    #     # A GET request resets the state of the wizard...
    #     self.client.get(reverse('two_factor:login'))

    #     # ...so there is no user in this request anymore. As the login flow
    #     # depends on a user being present, this should be handled gracefully.
    #     response = self._post({'token-otp_token': '123456',
    #                            'login_view-current_step': 'token'})
    #     self.assertContains(response, 'Password:')

    #     # Check that a message was logged.
    #     mock_logger.warning.assert_called_with(
    #         "Requested step '%s' is no longer valid, returning to last valid "
    #         "step in the wizard.",
    #         'token')

    # @mock.patch('two_factor.views.utils.logger')
    # def test_login_different_user_on_existing_session(self, mock_logger):
    #     """
    #     This test reproduces the issue where a user is logged in and a different user
    #     attempts to login.
    #     """
    #     self.create_user()
    #     self.create_user(username='vedran@example.com')

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

    #     response = self._post({'auth-username': 'vedran@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertRedirects(response, resolve_url(settings.LOGIN_REDIRECT_URL))

    # def test_missing_management_data(self):
    #     # missing management data
    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret'})

    #     # view should return HTTP 400 Bad Request
    #     self.assertEqual(response.status_code, 400)

    # def test_no_password_in_session(self):
    #     self.create_user()
    #     self.enable_otp()

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')

    #     session_contents = json.dumps(list(self.client.session.items()))

    #     self.assertNotIn('secret', session_contents)

    # def test_login_different_user_with_otp_on_existing_session(self):
    #     self.create_user()
    #     vedran_user = self.create_user(username='vedran@example.com')
    #     device = vedran_user.totpdevice_set.create(name='default',
    #                                         key=random_hex())

    #     response = self._post({'auth-username': 'bouke@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertRedirects(response,
    #                          resolve_url(settings.LOGIN_REDIRECT_URL))

    #     response = self._post({'auth-username': 'vedran@example.com',
    #                            'auth-password': 'secret',
    #                            'login_view-current_step': 'auth'})
    #     self.assertContains(response, 'Token:')
    #     response = self._post({'token-otp_token': totp(device.bin_key),
    #                            'login_view-current_step': 'token',
    #                            'token-remember': 'on'})
    #     self.assertRedirects(response,
    #                          resolve_url(settings.LOGIN_REDIRECT_URL))
