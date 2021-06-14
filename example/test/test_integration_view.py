#En este archivo vamos a hacer los integration test
import json
from django import urls

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


from .utils import UserMixin


class LoginTest(UserMixin, TestCase):

    def assert_url(self, expected_url):
        assert self.webdriver.current_url == self.base_url + expected_url

    def setUp(self):
        # Create a new Chrome session
        self.webdriver = webdriver.Chrome(ChromeDriverManager().install())
        self.webdriver.implicitly_wait(30)
        self.webdriver.maximize_window()

        # Webauthn Simulator
        self.setup_virtual_authenticator()

        self.base_url = 'https://dev.mypc.test'

   
    def tearDown(self):
        # Logout 
        logout = self.webdriver.find_element_by_xpath("//a[@href='/account/logout/']")
        logout.click()
        
        self.webdriver.quit()

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
    
    def test_valid_login(self):
        # Registro nuevo user
        register_url = '/account/register/'
        self.webdriver.get(self.base_url + register_url)

        # Completa campos
        username = self.webdriver.find_element_by_id('id_username')
        username.clear()
        username.send_keys("user-login-definitivo")

        password = self.webdriver.find_element_by_id('id_password1')
        password.clear()
        password.send_keys("user-login-definitivo")
        
        confirm_password = self.webdriver.find_element_by_id('id_password2')
        confirm_password.clear()
        confirm_password.send_keys("user-login-definitivo")

        button_register = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_register.click()
        
        self.assert_url('/account/register/done/')
        
        # Navigate into aplication login page
        login_url = "https://dev.mypc.test/account/login/"
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
        
        # Logout 
        logout = self.webdriver.find_element_by_xpath("//a[@href='/account/logout/']")
        logout.click()

        # Navigate into aplication login page
        login_url = "https://dev.mypc.test/account/login/"
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

         # Tengo que esperar que abra la llave
        try:
            delay = 8 #Seconds
            token_opt = WebDriverWait(self.webdriver, delay).until(EC.url_contains('https://dev.mypc.test/account/two_factor/'))
            print("Page is ready")
        except TimeoutException:
            print("Se mamo: " + str(TimeoutException))

        # Navigate into register two factor device page 
        register_url = "https://dev.mypc.test/account/two_factor/"
        self.webdriver.get(register_url)
        button_add_new_device = self.webdriver.find_element_by_xpath("//a[@href='/account/two_factor/setup/']")
        button_add_new_device.click()
        redirect_url = '/account/two_factor/setup/'
        self.assert_url(redirect_url)
        
        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Select wizard -> webauthn
        webauthn_input = self.webdriver.find_element_by_xpath("//input[@value='webauthn']")
        webauthn_input.click()
        button_next = self.webdriver.find_element_by_xpath("//button[@class='btn btn-primary']")
        button_next.click()
        redirect_url = '/account/two_factor/setup/'
        self.assert_url(redirect_url)
    
       
        
       





