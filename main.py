
from src.chromedriver import Chromedriver

chrome = Chromedriver()
chrome.get("https://www.google.com/")
input("hold")
 

# from src.chromedriver.os_utils import OSUtils

# print(OSUtils.get_root_directory_path()) 