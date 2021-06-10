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
    def _post(self, data=None):
        return self.client.post(reverse('two_factor:login'), data=data)
    
    def assert_urls(self,redirect_url):
       return self.assertEquals(self.webdriver.current_url,redirect_url)

    @classmethod
    def setUp(self):
        # Create a new Chrome session
        self.webdriver = webdriver.Chrome(ChromeDriverManager().install())
        self.webdriver.implicitly_wait(30)
        self.webdriver.maximize_window()
        
        # Navigate into aplication
        self.webdriver.get("https://dev.mypc.test/")
        options = self.webdriver.ChromeOptions()

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
        username.send_keys("userLogin")

        password = self.webdriver.find_element_by_id('id_auth-password')
        password.clear()
        password.send_keys("userLogin")

        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Navegate into aplication two_factor's device register
        redirect_url = 'https://dev.mypc.test/account/two_factor/'
        self.assert_urls(redirect_url)
        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//a[@class='btn btn-primary']")
        button_next.click()

        # Confirm the creation of the second factor device
        redirect_url = 'https://dev.mypc.test/account/two_factor/setup/'
        self.assert_urls(redirect_url)
        
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Select wizard -> webauthn
        redirect_url = 'https://dev.mypc.test/account/two_factor/setup/'
        self.assert_urls(redirect_url)
        
        webauthn_input = self.webdriver.find_element_by_xpath("//input[@value='webauthn']")
        webauthn_input.click()
        button_next = self.webdriver.find_element_by_xpath("//button[@class='btn btn-primary']")
        button_next.click()
        
        # Agregar como usar webauthn en chrome, evitar la trampa.
        # Init The emulator Webauthn device in chrome

        


        # Wait for authenticator(webauthn) //NO FUNCIONA//
        try:
            delay = 8 #Seconds
            token_opt = WebDriverWait(self.webdriver, delay).until(EC.url_contains('https://dev.mypc.test/account/two_factor/complete/'))
            print("Page is ready")
        except TimeoutException:
            print("Se mamo: " + str(TimeoutException))
        
        complete = self.webdriver.find_element_by_xpath("//a[@class='float-right btn btn-link']")
        complete.click()

        # Confirmation
        redirect_url = 'https://dev.mypc.test/account/two_factor/'
        self.assert_urls(redirect_url)

class RegisterWebAuthnTest(UserMixin, TestCase):
    def _post(self, data=None):
        return self.client.post(reverse('two_factor:login'), data=data)
    
    def assert_urls(self,redirect_url):
       return self.assertEquals(self.webdriver.current_url,redirect_url)

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

    def test_not_register_the_same_device(self):
        # Navigate into aplication login page
        login_url = "https://dev.mypc.test/account/login/"
        self.webdriver.get(login_url)
        self.assert_urls(login_url)

        # Completed Form
        username = self.webdriver.find_element_by_id('id_auth-username')
        username.clear()
        username.send_keys("user2")

        password = self.webdriver.find_element_by_id('id_auth-password')
        password.clear()
        password.send_keys("user2")

        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        
        # Enable virtual Authenticator
        enable_ = self.webdriver.execute_cdp_cmd('WebAuthn.enable',{})
        # Create new Authenticator
        virtual_authenticator_options = {
            'protocol' : 'u2f',
            'transport' : 'usb',
        }
        
        options = self.webdriver.execute_cdp_cmd('WebAuthn.addVirtualAuthenticator', {'options' : virtual_authenticator_options})
        
        # Use the authenticator
        options['enabled'] = True 
        breakpoint()
        self.webdriver.execute_cdp_cmd('WebAuthn.setUserVerified', options)
        
        #breakpoint()
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
        redirect_url = 'https://dev.mypc.test/account/two_factor/setup/'
        self.assert_urls(redirect_url)
        
        # "Next" Clicked
        button_next = self.webdriver.find_element_by_xpath("//button[@type='submit']")
        button_next.click()

        # Select wizard -> webauthn
        webauthn_input = self.webdriver.find_element_by_xpath("//input[@value='webauthn']")
        webauthn_input.click()
        button_next = self.webdriver.find_element_by_xpath("//button[@class='btn btn-primary']")
        button_next.click()
        redirect_url = 'https://dev.mypc.test/account/two_factor/setup/'
        self.assert_urls(redirect_url)



