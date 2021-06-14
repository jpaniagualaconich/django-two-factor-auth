from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from .utils import UserMixin


class WebAuthnFlowTest(UserMixin, StaticLiveServerTestCase):
    port = 8000
    base_url = 'https://localhost'

    def assert_url(self, expected_url):
        assert self.webdriver.current_url == self.base_url + expected_url

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.webdriver = webdriver.Chrome(ChromeDriverManager().install())
        cls.webdriver.implicitly_wait(10)
   
    @classmethod
    def tearDownClass(cls):
        cls.webdriver.quit()
        super().tearDownClass()

    def setup_virtual_authenticator(self):
        # Enable virtual Authenticator
        enable_ = self.webdriver.execute_cdp_cmd('WebAuthn.enable',{})
        
        # Create new Authenticator
        virtual_authenticator_options = {
            'protocol' : 'u2f',
            'transport' : 'usb',
        }
        self.virtual_authenticator = self.webdriver.execute_cdp_cmd('WebAuthn.addVirtualAuthenticator', {'options' : virtual_authenticator_options})
        #self.webdriver.execute_cdp_cmd('WebAuthn.AutomaticPresenceSimulation', {'authenticatorId' : options['authenticatorId']})
    
    def test_attestation_assertion_attestation(self):
        self.setup_virtual_authenticator()

        self.create_user()
        
        # Navigate into aplication login page
        login_url = self.base_url + "/account/login/"
        self.webdriver.get(login_url)
        self.assert_url('/account/login/')

        # Completed Form
        username = self.webdriver.find_element_by_id('id_auth-username')
        username.clear()
        username.send_keys("user-login-definitivo")

        password = self.webdriver.find_element_by_id('id_auth-password')
        password.clear()
        password.send_keys("user-login-definitivo")

        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Navegate into aplication two_factor's device register
        self.assert_url('/account/two_factor/')
        
        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//a[@class='btn btn-primary']")
        button_next.click()

        # Confirm the creation of the second factor device
        self.assert_url('/account/two_factor/setup/')
        
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Select wizard -> webauthn
        self.assert_url('/account/two_factor/setup/')
        
        webauthn_input = self.webdriver.find_element_by_xpath("//input[@value='webauthn']")
        webauthn_input.click()
        button_next = self.webdriver.find_element_by_xpath("//button[@class='btn btn-primary']")
        button_next.click()
        

        # Wait for authenticator(webauthn)
        try:
            delay = 8 #Seconds
            token_opt = WebDriverWait(self.webdriver, delay).until(EC.url_contains('https://dev.mypc.test/account/two_factor/complete/'))
            print("Page is ready")
        except TimeoutException:
            print("Se mamo: " + str(TimeoutException))
        
        complete = self.webdriver.find_element_by_xpath("//a[@class='float-right btn btn-link']")
        complete.click()

        # Confirmation
        self.assert_url('/account/two_factor/')
