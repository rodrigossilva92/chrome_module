import sys
import os
import psutil
import signal
import platform
import subprocess
import zipfile
import urllib.request
from io import BytesIO

class OSUtils:
    """
    Class to handle some operational system functionalities
    """
    LINUX   = "linux"
    WINDOWS = "win"
    MAC     = "mac"
    
    @staticmethod
    def get_os_type() -> str:
        """
        Returns the operational system type
        """
        os_type = sys.platform
        if "linux" in os_type:
            return OSUtils.LINUX
        if os_type == "win32":
            return OSUtils.WINDOWS
        if os_type == "darwin":
            return OSUtils.MAC
        raise Exception(os_type)
    
    @staticmethod
    def get_os_architecture() -> str:
        """
        Returns the operational system architecture
        """
        os_architecture = platform.machine()
        if os_architecture.endswith("64"):
            return "64"
        if os_architecture.endswith("32"):
            return "32"
        raise Exception(f"Architecture {os_architecture} not defined.")
    
    @staticmethod
    def get_os_definition() -> str:
        """
        Returns the operational system type and architecture
        """
        os_type = OSUtils.get_os_type()
        os_architecture = OSUtils.get_os_architecture()
        return f"{os_type}{os_architecture}"
    
    @staticmethod
    def send_terminal_command(cmd:str) -> str:
        """
        Execute a given terminal command and returns the respective output
        """
        with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                shell=True
            ) as stream:
            return stream.communicate()[0].decode()

    @staticmethod
    def download_from_url(url:str) -> BytesIO:
        """
        Downloads a file from a given url into a buffer
        """
        response = urllib.request.urlopen(url)
        return BytesIO(response.read())
    
    @staticmethod
    def extract_zip_file(file:BytesIO, path:str):
        """
        Extracts a file from a buffer into a given system path
        """
        with zipfile.ZipFile(file, 'r') as zip_file:
            zip_file.extractall(path)
    
    @staticmethod
    def kill_process_children(script_name:str):
        """
        Kills all children processes from a given process/script name
        """
        for pid in OSUtils.get_process_ids(script_name):
            OSUtils.kill_process_id_children(pid)
    
    @staticmethod
    def kill_process_id_children(pid:int):
        """
        Kills all children processes from a given process id
        """
        for cid in OSUtils.get_children_ids(pid):
            OSUtils.kill_process(cid)

    @staticmethod
    def get_process_ids(process_name:str) -> list[int]:
        """
        Returns the found ids from a given process/script
        """
        cmd = "ps -ef | grep " + process_name + " | awk '{print $2}'"
        cmd_output = OSUtils.send_terminal_command(cmd)
        process_ids = [int(line) for line in cmd_output.splitlines()]
        return process_ids
    
    @staticmethod
    def get_children_ids(pid:int) -> list[int]:
        """
        Returns the children ids from a given process id
        """
        try:
            process = psutil.Process(pid)
            children_ids = list()
            for child in process.children(recursive=True):
                print(child.name())
                children_ids.append(child.pid)
            return children_ids
        except Exception as e:
            print(e)
            return list()
    
    @staticmethod
    def kill_process(pid:int):
        """
        Kills a process by its given id
        """
        os.kill(pid, signal.SIGKILL)

    @staticmethod
    def get_root_directory_path() -> str:
        """
        Returns the project root directory
        """
        path_file = sys.modules['__main__'].__file__
        path_dir = os.path.dirname(path_file)
        return path_dir
    
    @staticmethod
    def get_root_process_name() -> str:
        """
        Returns the project root script name
        """
        path_file = sys.modules['__main__'].__file__
        name_file = os.path.basename(path_file)
        return name_file
        