import os
import unittest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .utils import UserMixin


class WebAuthnE2ETest(UserMixin, StaticLiveServerTestCase):
    port = 8000
    base_url = 'https://localhost'

    def assert_url(self, expected_url):
        assert self.webdriver.current_url == self.base_url + expected_url

    def setUp(self):
        if not os.environ.get('E2E_TESTS'):
            return self.skipTest(f'E2E_TESTS environment variable is not set')

        super().setUp()

        self.webdriver = webdriver.Chrome(ChromeDriverManager().install())
        self.webdriver.implicitly_wait(10)
   
    def tearDown(self):
        self.webdriver.quit()
        super().tearDown()

    def setup_virtual_authenticator(self):
        enable_ = self.webdriver.execute_cdp_cmd('WebAuthn.enable',{})
        virtual_authenticator_options = {
            'protocol' : 'u2f',
            'transport' : 'usb',
        }
        self.virtual_authenticator = self.webdriver.execute_cdp_cmd(
            'WebAuthn.addVirtualAuthenticator', {'options' : virtual_authenticator_options})
    
    def wait_for(self, tag, timeout=8):
        WebDriverWait(self.webdriver, timeout).until(
            lambda driver: driver.find_element(By.TAG_NAME, tag))

    def do_login(self):
        login_url = self.base_url + "/account/login/"
        self.webdriver.get(login_url)
        self.assert_url('/account/login/')

        username = self.webdriver.find_element(By.ID, 'id_auth-username')
        username.clear()
        username.send_keys("bouke@example.com")

        password = self.webdriver.find_element(By.ID, 'id_auth-password')
        password.clear()
        password.send_keys("secret")

        button_next = self.webdriver.find_element(By.XPATH, "//button[@type='submit']")
        button_next.click()       

        self.wait_for('body')

    def test_webauthn_attestation_and_assertion(self):
        self.setup_virtual_authenticator()

        self.create_user()
        
        self.do_login()

        # registering the webauthn authenticator as a second factor  
        self.webdriver.find_element(By.XPATH, '//a[contains(text(),\'Enable Two-Factor Authentication\')]').click()  
        self.wait_for('body')

        self.webdriver.find_element(By.XPATH, '//h1[text()=\'Enable Two-Factor Authentication\']')
        self.webdriver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait_for('body')

        self.webdriver.find_element(By.XPATH, "//input[@value='webauthn']").click()
        self.webdriver.find_element(By.XPATH, "//button[@class='btn btn-primary']").click()
        WebDriverWait(self.webdriver, 8).until(EC.url_contains('/account/two_factor/setup/complete/'))
        self.wait_for('body')

        self.webdriver.find_element(
            By.XPATH,
            '//p[text()="Congratulations, you\'ve successfully enabled two-factor authentication."]',
        )
        self.webdriver.get(self.base_url + "/account/logout/")
        self.wait_for('body')

        # using the webauthn authenticator to log in
        self.do_login()

        WebDriverWait(self.webdriver, 8).until(EC.url_contains('/account/two_factor/'))
        self.wait_for('body')

        # attempting to register an already registered authenticator
        self.webdriver.find_element(By.LINK_TEXT, "Add device").click()
        self.wait_for('body')

        self.webdriver.find_element(By.XPATH, '//h1[text()=\'Enable Two-Factor Authentication\']')
        self.webdriver.find_element(By.XPATH, "//button[@type='submit']").click()
        self.wait_for('body')

        self.webdriver.find_element(By.XPATH, "//input[@value='webauthn']").click()
        self.webdriver.find_element(By.XPATH, "//button[@class='btn btn-primary']").click()
        self.wait_for('body')

        self.webdriver.find_element_by_xpath("//p[@class='text-danger']")
