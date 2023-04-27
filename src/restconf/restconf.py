import requests
import os
import sys

def get_models():
    # Replace these values with your device's information
    device_ip_port = "localhost:8443"
    username = os.environ["RESTCONF_USERNAME"]
    password = os.environ["RESTCONF_PASSWORD"]
    
    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }
    
    #yang_url = f"https://{device_ip_port}/restconf/data/Cisco-IOS-XE-native:native"
    #yang_url = f"https://{device_ip_port}/restconf/tailf/modules/Cisco-IOS-XE-interfaces/2019-09-30"
    yang_url = f"https://{device_ip_port}/restconf/data/ietf-yang-library:modules-state"
    
    response = requests.get(yang_url, auth=(username, password), headers=headers, verify=False)
    return response.text
    #
    ## Save the YANG model to a local file
    #with open(f"{yang_module}-{yang_revision}.yang", "w") as f:
    #    f.write(response.text)
    #

if __name__ == '__main__':
    if os.getenv('RESTCONF_USERNAME') is None or os.getenv('RESTCONF_USERNAME') == '' or os.getenv('RESTCONF_PASSWORD') is None or os.getenv('RESTCONF_PASSWORD') == '':
        print("Please set the RESTCONF_USERNAME and RESTCONF_PASSWORD environment variable")
        sys.exit(1)
    
    models=get_models()
    print(models)
	#print(response.json())

