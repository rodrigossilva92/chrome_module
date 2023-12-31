import os
import psutil
from time import sleep
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .chromedriver_manager import ChromedriverManager
from .os_utils import OSUtils

class Chromedriver:
    """
    Class to handle selenium chromedriver 
    """
    TIMEOUT = 10    # seconds
    CHROME_PROCESSES = ['chrome',
                        'chromedriver',
                        'chrome.exe',
                        'chromedriver.exe']

    def __init__(self, path_chromedriver:str=None, headless:bool=False, kill_chrome:bool=True, download:bool=False, path_downloads:str=None, chrome_arguments:list=None):
        """
        class constructor
        """
        self.path_chromedriver = os.path.abspath(path_chromedriver) if path_chromedriver is not None else None
        self.headless = headless
        self.kill_chrome = kill_chrome
        self.download = download
        self.path_downloads = os.path.abspath(path_downloads) if path_downloads is not None else OSUtils.get_root_directory_path()
        self.chrome_arguments = list() if chrome_arguments is None else chrome_arguments

        self.__start_driver()                

    def __del__(self):
        """
        Class destructor
        """
        if self.kill_chrome:
            Chromedriver.kill_chrome_children()
        if hasattr(self, 'driver'):
            self.driver.quit()                        
    
    @staticmethod
    def kill_chrome_children(pid:int=None):
        """
        Kills chromedriver process children
        """
        process = psutil.Process() if pid is None else psutil.Process(pid)
        for child in process.children(recursive=True):
            if child.name() in Chromedriver.CHROME_PROCESSES:
                child.kill()                      
    
    def __start_driver(self):
        """
        Starts the driver
        """
        chrome_options = ChromeOptions()               
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')            
        chrome_options.add_argument('--disable-extensions')

        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-translate')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')
        chrome_options.add_argument('--ignore-certificate-errors-spki-list')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--allow-insecure-localhost')

        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')

   
        for argument in self.chrome_arguments:
            chrome_options.add_argument(argument)

        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--window-size=1920,1080')
        else:            
            chrome_options.add_argument('--start-maximized')

        if self.download:
            if self.path_chromedriver is None:
                prefs = {
                    "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], # Disable Chrome's PDF Viewer                
                    "download.extensions_to_open": "applications/pdf",                       
                    "download.default_directory": self.path_downloads,
                }
            else:
                prefs = {
                    "download.prompt_for_download": False,
                    "plugins.always_open_pdf_externally": True,
                    "download.default_directory": self.path_downloads
                }
            chrome_options.add_experimental_option('prefs', prefs)
            self.driver.set_page_load_timeout(60*3)
            if self.headless:
                self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
                params = {
                    'cmd':'Page.setDownloadBehavior',
                    'params': {
                        'behavior': 'allow',
                        'downloadPath': self.path_downloads
                    }
                }
                self.driver.execute("send_command", params)        
    
        try:
            if self.path_chromedriver is None:
                self.driver = Chrome(options=chrome_options)
            else:
                chrome_service = Service(executable_path=self.path_chromedriver)
                self.driver = Chrome(service=chrome_service,
                                     options=chrome_options)
        except WebDriverException:
            self.path_chromedriver = ChromedriverManager.manage_chromedriver(self.path_chromedriver)
            self.__start_driver()
        
    #####################################################################################################################################
    ##

    def get(self, url:str):
        """
        Access a given url
        """
        self.driver.get(url)
    
    def refresh(self):
        """
        Refreshes the page
        """
        self.driver.refresh()
    
    def click(self, xpath:str):
        """
        Clicks in a given element
        """
        WebDriverWait(self.driver, Chromedriver.TIMEOUT).until(EC.presence_of_element_located((By.XPATH, xpath)))
        self.driver.find_element(By.XPATH, value=xpath).click()
        sleep(.25)

    def click_index(self, xpath:str, index=int):
        """
        Clicks in a specific element given index. Helps when there are a lot of similar xpaths for an element
        """
        elements = self.driver.find_elements(By.XPATH, value=xpath)
        elements[index].click()
    
    def escape(self):
        """
        Presses ESC
        """
        sleep(.5)
        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()       

    def press_tab(self, xpath:str):
        """
        Presses TAB
        """
        self.send_keys(xpath=xpath, keys=Keys.TAB)

    def send_keys(self, xpath:str, keys:str):
        """
        Sends the given string to an element
        """
        WebDriverWait(self.driver, Chromedriver.TIMEOUT).until(EC.presence_of_element_located((By.XPATH, xpath)))
        self.driver.find_element(By.XPATH, value=xpath).clear()
        self.driver.find_element(By.XPATH, value=xpath).send_keys(Keys.HOME+keys)
        sleep(.25)    
    
    def drop_down(self, xpath:str, keys:str):
        """
        Selects a given string from a dropdown element
        """
        WebDriverWait(self.driver, Chromedriver.TIMEOUT).until(EC.presence_of_element_located((By.XPATH, xpath)))
        self.driver.find_element(By.XPATH, value=xpath).click()
        sleep(.1)
        self.driver.find_element(By.XPATH, value=xpath).send_keys(keys+Keys.ESCAPE)
        sleep(.75)
    
    def get_element_attribute(self, xpath:str, attribute:str) -> str:
        """
        Returns the given attribute of a given element xpath
        """
        WebDriverWait(self.driver, Chromedriver.TIMEOUT).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = self.driver.find_element(By.XPATH, value=xpath)
        return element.get_attribute(attribute)

    def get_elements_attribute(self, xpath:str, attribute:str) -> list:
        """
        Return a list of a given attribute for a given element xpath
        """
        WebDriverWait(self.driver, Chromedriver.TIMEOUT).until(EC.presence_of_element_located((By.XPATH, xpath)))
        elements = self.driver.find_elements(By.XPATH, value=xpath)
        if len(elements) > 0:
            return [e.get_attribute(attribute) for e in elements]
        return []
    
    def check_attribute_exists(self, xpath:str, attribute:str) -> bool:
        element = self.get_element_attribute(xpath, attribute)
        return True if element else False

    def check_element_exists(self, xpath:str) -> bool:
        """
        Verifies if a given element xpath exists
        """
        elements = self.driver.find_elements(By.XPATH, value=xpath)
        if len(elements) > 0:
            return True
        return False

    def get_elements(self, xpath:str) -> list:
        """
        Returns the list of elements found for a given xpath
        """
        return self.driver.find_elements(By.XPATH, value=xpath)

    def get_element_text(self, xpath:str) -> str:
        """
        Returns the text of a given xpath element
        """
        element = self.driver.find_element(By.XPATH, value=xpath)
        return element.text
    
    def get_elements_text(self, xpath:str) -> list:
        """
        Returns a list of text of a given xpath element
        """
        elements = self.driver.find_elements(By.XPATH, value=xpath)
        return [e.text for e in elements]
    
    def screenshot(self, path_file:str):
        """
        Takes a screenshot and saves in the given path
        """
        self.driver.save_screenshot(path_file)
    
    def handle_windows(self) -> tuple[str,str]:
        """
        Returns the name of the main window and the pop up window when there is necessity for it
        """
        main_window = self.driver.window_handles[0]
        pop_up = self.driver.window_handles[1]
        return main_window, pop_up

    def switch_window(self, window:str):
        """
        Switches the driver to the given window
        """
        self.driver.switch_to.window(window)
        