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
        enable_ = self.webdriver.execute_cdp_cmd('WebAuthn.enable',{})
        virtual_authenticator_options = {
            'protocol' : 'u2f',
            'transport' : 'usb',
        }
        self.virtual_authenticator = self.webdriver.execute_cdp_cmd('WebAuthn.addVirtualAuthenticator', {'options' : virtual_authenticator_options})
    
    def wait_for(self, tag, timeout=8):
        WebDriverWait(self.webdriver, timeout).until(
            lambda driver: driver.find_element_by_tag_name(tag))

    def do_login(self):
        login_url = self.base_url + "/account/login/"
        self.webdriver.get(login_url)
        self.assert_url('/account/login/')

        username = self.webdriver.find_element_by_id('id_auth-username')
        username.clear()
        username.send_keys("bouke@example.com")

        password = self.webdriver.find_element_by_id('id_auth-password')
        password.clear()
        password.send_keys("secret")

        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()       

    def test_attestation_assertion_attestation(self):
        self.setup_virtual_authenticator()

        self.create_user()
        
        self.do_login()

        self.wait_for('body')
        self.webdriver.find_element(By.XPATH, '//button[text()=\'Enable Two-Factor Authentication\']').click()  
        
        self.wait_for('body')
        self.webdriver.find_element(By.XPATH, '//h1[text()=\'Enable Two-Factor Authentication\']')
        self.webdriver.find_element_by_xpath("//button[@type='submit']").click()

        self.wait_for('body')
        self.webdriver.find_element_by_xpath("//input[@value='webauthn']").click()
        self.webdriver.find_element_by_xpath("//button[@class='btn btn-primary']").click()
        
        self.wait_for('body')
        WebDriverWait(self.webdriver, 8).until(EC.url_contains('/account/two_factor/complete/'))
        self.webdriver.find_element_by_xpath("//a[@class='float-right btn btn-link']").click()

        self.wait_for('body')
        self.webdriver.find_element(By.XPATH, '//p[text()="Congratulations, you\'ve successfully enabled two-factor authentication."]')
        self.webdriver.get(self.base_url + "/account/logout/")

        self.wait_for('body')
        self.do_login()

        self.wait_for('body')
        # self.webdriver.find_element_by_id("id_token-otp_token")
        WebDriverWait(self.webdriver, 8).until(EC.url_contains('/account/two_factor/'))
        self.webdriver.find_element_by_link_text("Add device").click()

        self.wait_for('body')
        self.webdriver.get(self.base_url() + "/account/two_factor/setup/")
        self.webdriver.find_element(By.XPATH, '//button[text()="Add device"]').click()
        
        self.wait_for('body')
        self.webdriver.find_element_by_xpath("//button[@type='submit']").click()

        self.wait_for('body')
        self.webdriver.find_element_by_xpath("//input[@value='webauthn']").click()
        self.webdriver.find_element_by_xpath("//button[@class='btn btn-primary']").click()

        # message = 'InvalidStateError: The user attempted to register an authenticator that contains one of the credentials already registered with the relying party.'
        # assert  message == self.webdriver.find_element_by_xpath("//p[@class='text-danger']")