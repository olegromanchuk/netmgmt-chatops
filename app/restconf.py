import requests
import os
import sys
import logging
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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
    
class RestConfException(Exception):
    def __init__(self, message, dict_data):
        super().__init__(message)
        self.dict_data = dict_data


                      
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
                raise ValueError(f"Authentication failed. Please check the RESTCONF_USERNAME and RESTCONF_PASSWORD environment variable. Error: {e}")
            raise ConnectionError(f"ConnectionError: {e}")
        return response.json()['Cisco-IOS-XE-native:hostname']

    def get_interfaces(self):
            # yang_url = f"https://{self.device_ip_port}/restconf/data/Cisco-IOS-XE-native:native/interface/Port-channel=5/ip/address"
            yang_url = f"https://{self.device_ip_port}/restconf/data/Cisco-IOS-XE-native:native/interface"
            restconf_logger.debug(f"sending GET to restconf host. url: {yang_url}, headers:{self.headers}")
            response = requests.get(yang_url, auth=self.auth, headers=self.headers, verify=False)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 401:
                    raise ValueError(f"Authentication failed. Please check the RESTCONF_USERNAME and RESTCONF_PASSWORD environment variable. Error: {e}")
                raise ConnectionError(f"ConnectionError: {e}")
            return response.json()
    

    def create_interface_portchannel(self, interface_name, interface_ip, interface_mask):
        if interface_name is None or interface_name == '':
            raise ValueError('interface_name is required')
        
        interface_type = 'Port-channel'

        # Define the URL for the POST request
        yang_url = f"https://{self.device_ip_port}/restconf/data/Cisco-IOS-XE-native:native/interface/"
       
        # Define the body of the POST request
        payload = {
            "Cisco-IOS-XE-native:Port-channel": {
                        "name": interface_name,
                        "description": interface_name,
                        "ip": {
                            "address": {
                                "primary": {
                                    "address": interface_ip,
                                    "mask": interface_mask
                                }
                            }
                        }            
            }
        }

        restconf_logger.debug(f"sending POST to restconf host. url: {yang_url}, headers:{self.headers}, payload: {payload}")
        
        response = requests.post(yang_url, auth=self.auth, headers=self.headers, json=payload, verify=False)
        restconf_logger.debug(f"Got result. Status code: {response.status_code}, response_body: {response.text}")


        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            restconf_logger.debug(f"Got exception. Status code: {response.status_code}, error: {e}, response_body: {response.json()}")
            if response.status_code == 400:
                msgObj = {"error-tag": "invalid-value",
                              "error-message": response.json()
                        }
                raise RestConfException(f"client error. Error: {e}", msgObj)
            if response.status_code == 401:
                msgObj = {"error-tag": "authentication-failed",
                              "error-message": response.json()
                        }
                raise RestConfException(f"Authentication failed. Please check the RESTCONF_USERNAME and RESTCONF_PASSWORD environment variable. Error: {e}", msgObj)
            if response.status_code == 409:
                msgObj = {"error-tag": "",
                    "error-message": response.json()
                    }
                if response.json()['errors']['error'][0]['error-tag'] == 'data-exists':
                    msgObj["error-tag"]="data-exists"
                raise RestConfException(f"client conflict. Error: {e}", msgObj)
            raise ConnectionError(f"ConnectionError: {e}")
        
        restconf_logger.debug(f"response status code: {response.status_code}, response_body: {response.text}")

        # Check if the request was successful
        if response.status_code == 201:
            return_msg=f"Interface {interface_type} {interface_name} created successfully."
        else:
            msgObj = {"error-tag": "unknown-error",
                    "error-message": response.text,
                    "status-code": response.status_code
                    }
            restconf_logger.error(f"Failed to create interface. Status code: {response.status_code}. Response: {response.text}.")
            raise RestConfException(f"Failed to create interface", msgObj)

        return return_msg

    
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

