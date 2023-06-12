import os
import re
import urllib.request
import xml.etree.ElementTree as ET

from .os_utils import OSUtils

class ChromedriverManager:
    VERSION_PATTERN = r"\d+\.\d+\.\d+\.\d+"
    CHROMEDRIVER_NAME_MAPPING = {
        "linux": "chromedriver",
        "win": "chromedriver.exe"
    }

    @classmethod
    def get_chrome_version(cls) -> str:
        cmd_chrome_version_map = {
            OSUtils.LINUX: r"google-chrome --version",
            OSUtils.WINDOWS: ['powershell', '-command', '$(Get-ItemProperty -Path Registry::HKEY_CURRENT_USER\\Software\\Google\\chrome\\BLBeacon).version'],
            OSUtils.MAC: r"/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version",
        }
        cmd_version = cmd_chrome_version_map[OSUtils.get_os_type()]
        cmd_return = OSUtils.send_terminal_command(cmd_version)
        print(cmd_return)
        version = re.search(cls.VERSION_PATTERN,
                            cmd_return).group(0)
        return version
    
    @classmethod
    def get_chromedriver_version(cls, path_chromedriver:str) -> str:
        abs_path = os.path.abspath(path_chromedriver)
        cmd = f"{abs_path} --version"
        cmd_return = OSUtils.send_terminal_command(cmd)
        print(cmd_return)
        version = re.search(cls.VERSION_PATTERN, 
                            cmd_return).group(0)
        return version
    
    @classmethod
    def get_major_version(cls, version:str) -> str:
        major_version = version.split('.')[0]
        return major_version

    @classmethod
    def check_versions_compatibilty(cls, path_chromedriver:str) -> bool:
        try:
            major_version_chrome = cls.get_major_version(cls.get_chrome_version())
            major_version_chromedriver = cls.get_major_version(cls.get_chromedriver_version(path_chromedriver))
            return major_version_chrome == major_version_chromedriver
        except:
            return False
    
    @classmethod
    def download_chromedriver(cls, path_save_chromedriver:str) -> str:
        os.makedirs(path_save_chromedriver, exist_ok=True)
        os_url_mapping = {
            "linux": "linux64",
            "win": "win32"
        }

        os_type = os_url_mapping[OSUtils.get_os_type()]
        # chrome_major_version = cls.get_major_version(cls.get_chrome_version())
        chromedriver_download_version = cls.get_download_compatible_version()
        io_chromedriver = OSUtils.download_from_url("https://chromedriver.storage.googleapis.com/" + chromedriver_download_version + '/chromedriver_' + os_type + ".zip")
        OSUtils.extract_zip_file(io_chromedriver, path_save_chromedriver)
        path_chromedriver = os.path.join(path_save_chromedriver, cls.CHROMEDRIVER_NAME_MAPPING[OSUtils.get_os_type()])
        os.chmod(path_chromedriver, 0o744)       
        return path_chromedriver

    @classmethod
    def get_download_compatible_version(cls) -> str:
        chrome_major_version = cls.get_major_version(cls.get_chrome_version())
        response = urllib.request.urlopen("https://chromedriver.storage.googleapis.com").read()
        tree = ET.fromstring(response)
        for i in tree.iter("{http://doc.s3.amazonaws.com/2006-03-01}Key"):
            if i.text.find(chrome_major_version + '.') == 0:
                return i.text.split('/')[0]
        raise Exception(f"Chromedriver version '{chrome_major_version}' not found to download.")
    
    @classmethod
    def manage_chromedriver(cls, path_chromedriver:str) -> str:
        if path_chromedriver is None:
            path_chromedriver = OSUtils.get_root_directory_path()
        path_chromedriver = os.path.abspath(path_chromedriver)
        if os.path.isfile(path_chromedriver) and cls.CHROMEDRIVER_NAME_MAPPING[OSUtils.get_os_type()] == os.path.basename(path_chromedriver):
            if cls.check_versions_compatibilty(path_chromedriver):
                print("Chrome and chromedriver versions should be compatible.")            
                return path_chromedriver
            os.remove(path_chromedriver)
            path_dir_chromedriver = os.path.dirname(path_chromedriver)
        else:
            path_dir_chromedriver = path_chromedriver
            if not os.path.exists(path_dir_chromedriver):
                os.makedirs(path_dir_chromedriver, exist_ok=True)
            for file in os.listdir(path_dir_chromedriver):
                path_file = os.path.join(path_dir_chromedriver, file)
                if os.path.isfile(path_file) and cls.CHROMEDRIVER_NAME_MAPPING[OSUtils.get_os_type()] == file:
                    if cls.check_versions_compatibilty(path_file):
                        print("Chrome and chromedriver versions should be compatible.")     
                        return path_file
                    os.remove(path_file)
        path_chromedriver = cls.download_chromedriver(path_dir_chromedriver)    
        return path_chromedriver          
