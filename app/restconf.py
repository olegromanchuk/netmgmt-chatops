import requests
import os
import sys
import logging

# Create a custom logger
restconf_logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()

# Create formatters and add it to handlers
c_format = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
c_handler.setFormatter(c_format)

# Add handlers to the logger
restconf_logger.addHandler(c_handler)



if os.getenv('DEVICE_IP_PORT') is None or os.getenv('DEVICE_IP_PORT') == '' or os.getenv('RESTCONF_USERNAME') is None or os.getenv('RESTCONF_USERNAME') == '' or os.getenv('RESTCONF_PASSWORD') is None or os.getenv('RESTCONF_PASSWORD') == '':
    raise ValueError('Please set the RESTCONF_USERNAME and RESTCONF_PASSWORD and DEVICE_IP_PORT environment variable')

# device's information
device_username = os.environ["RESTCONF_USERNAME"]
device_password = os.environ["RESTCONF_PASSWORD"]
device_ip_port = os.environ["DEVICE_IP_PORT"]
    
class Device():
    def __init__(self, device_ip_port=device_ip_port, device_username=device_username, device_password=device_password, debug=False):
        self.device_username=device_username
        self.device_password=device_password
        self.device_ip_port=device_ip_port
        self.headers = {
                "Accept": "application/yang-data+json",
                "Content-Type": "application/yang-data+json"
            }
        self.auth=(self.device_username, self.device_password)
        if debug:
            restconf_logger.setLevel(logging.DEBUG)
        

    def get_hostname(self):
        yang_url = f"https://{self.device_ip_port}/restconf/data/Cisco-IOS-XE-native:native/hostname"
        restconf_logger.debug(f"sending GET to restconf host. url: {yang_url}, headers:{self.headers}")
        response = requests.get(yang_url, auth=self.auth, headers=self.headers, verify=False)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError(e)
            raise ConnectionError(f"ConnectionError: {e}")
        
        return response.json()['Cisco-IOS-XE-native:hostname']

    def get_interfaces(self):
            # yang_url = f"https://{self.device_ip_port}/restconf/data/Cisco-IOS-XE-native:native/interface/Port-channel=5/ip/address"
            yang_url = f"https://{self.device_ip_port}/restconf/data/Cisco-IOS-XE-native:native/interface"
            try:
                response = requests.get(yang_url, auth=self.auth, headers=self.headers, verify=False)
            except Exception as e:
                print(f"Got error: {e}")
            return response.json()
    
    def get_models(self):
        #yang_url = f"https://{device_ip_port}/restconf/data/Cisco-IOS-XE-native:native"
        #yang_url = f"https://{device_ip_port}/restconf/tailf/modules/Cisco-IOS-XE-interfaces/2019-09-30"
        yang_url = f"https://{self.device_ip_port}/restconf/data/ietf-yang-library:modules-state"
        
        response = requests.get(yang_url, auth=self.auth, headers=self.headers, verify=False)
        return response.text


if __name__ == '__main__':
    if os.getenv('RESTCONF_USERNAME') is None or os.getenv('RESTCONF_USERNAME') == '' or os.getenv('RESTCONF_PASSWORD') is None or os.getenv('RESTCONF_PASSWORD') == '':
        print("Please set the RESTCONF_USERNAME and RESTCONF_PASSWORD environment variable")
        sys.exit(1)

