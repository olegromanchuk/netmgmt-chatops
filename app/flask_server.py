#!/usr/bin/env python3

from flask import Flask
from flask import jsonify
from flask import request
from messenger import Messenger
from restconf import Device, RestConfException
from tabulate import tabulate
import datetime as dtc
import os
import sys


def get_hostname(debug=False):
    device = Device(debug=debug)
    hostname=''
    try:
        hostname = device.get_hostname()
    except Exception as e:
        app.logger.error(f"Error: 7001 failed to get hostname. Error: {e}")
        result_message = f"Error: 7001. Mgs: failed to get hostname: cannot connect to device"
        return result_message
    app.logger.debug(f"got hostname: {hostname}")
    return f"hostname: {hostname}"


def get_interfaces(debug=False):
    device = Device(debug=debug)
    interfaces_info=''
    try:
        interfaces_info = device.get_interfaces()
    except Exception as e:
        app.logger.error(f"Error: 7002 failed to get interfaces. Error: {e}")
        result_message = f"Error: 7002. Mgs: failed to get interfaces: cannot connect to device"
        return result_message
    app.logger.debug(f"got interfaces: {interfaces_info}")
    parsed_output = parse_interfaces(interfaces_info)
    return f"hostname: {parsed_output}"


def create_interface_via_device(debug=False, interface_name=None, interface_ip=None, interface_mask=None):
    if interface_name is None or interface_ip is None or interface_mask is None:
        app.logger.error(f"Error: 7004 failed to create interface. Error: interface_name, interface_ip, interface_mask must be provided")
        result_message = f"Error: 7004. Mgs: failed to create interface: interface_name, interface_ip, interface_mask must be provided"
        return result_message
    
    device = Device(debug=debug)
    result_message=''
    try:
        result_message = device.create_interface_portchannel(interface_name=interface_name, interface_ip=interface_ip, interface_mask=interface_mask)
    except Exception as e:
        if isinstance(e, ConnectionError):
            app.logger.error(f"Error: 7003 failed to create interface. Error: {e}")
            result_message = f"Error: 7003. Mgs: failed to create interface: cannot connect to device"
        if isinstance(e, RestConfException):
            app.logger.error(f"Error: 706x failed to create interface. Error: {e}. Details: {e.dict_data}")

            # form clear error message for user
            if e.dict_data["error-tag"]== "data-exists":
                result_message = f"Error: 7060. Mgs: creation failed. Object already exists."
            elif e.dict_data["error-tag"]== "authentication-failed":
                result_message = f"Error: 7061. Mgs: creation failed. Authentication failed."
            elif e.dict_data["error-tag"]== "invalid-value":
                result_message = f"Error: 7062. Mgs: creation failed. Restconf device rejected our request."
            elif e.dict_data["error-tag"]== "unknown-error":
                result_message = f"Error: 7063. Mgs: creation failed. Request was processed, but not 201 returned."
            else:
                result_message = f"Error: 7064. Mgs: failed to create interface. Restconf device rejected our request."

        elif isinstance(e, Exception):
            app.logger.error(f"Error: 7005 failed to create interface. Error: {e}")
    return result_message


def parse_interfaces(data):
    table_data = []

    # Extract GigabitEthernet interfaces
    try:
        for gig in data['Cisco-IOS-XE-native:interface']['GigabitEthernet']:
            if 'address' in gig['ip'] and 'primary' in gig['ip']['address'] and 'address' in gig['ip']['address']['primary']:
                table_data.append(["GigabitEthernet", gig['name'], gig.get('description', ""), gig['ip']['address']['primary']['address'], gig['ip']['address']['primary']['mask']])
    except KeyError:
        pass

    # Extract Port-channel interfaces
    try:
        for port in data['Cisco-IOS-XE-native:interface']['Port-channel']:
            if 'address' in port['ip'] and 'primary' in port['ip']['address'] and 'address' in port['ip']['address']['primary']:
                table_data.append(["Port-channel", port['name'], port.get('description', ""), port['ip']['address']['primary']['address'], port['ip']['address']['primary']['mask']])
    except KeyError:
        pass

    # Extract Port-channel-subinterface interfaces
    try:
        for sub_port in data['Cisco-IOS-XE-native:interface']['Port-channel-subinterface']['Port-channel']:
            if 'address' in sub_port['ip'] and 'primary' in sub_port['ip']['address'] and 'address' in sub_port['ip']['address']['primary']:
                table_data.append(["Port-channel-subinterface", sub_port['name'], sub_port.get('description', ""), sub_port['ip']['address']['primary']['address'], sub_port['ip']['address']['primary']['mask']])
    except KeyError:
        pass
        
    return tabulate(table_data, headers=["Type", "Name", "Description", "IP Address", "Mask"], tablefmt="grid")

    

app = Flask(__name__)

@app.route('/hello/<string:name>', methods=['GET', 'POST'])
def welcome(name):
    return "Hello " + name

@app.route('/backup', methods=['GET', 'POST'])
def backupRoute():
    return "received request for backup"

@app.route('/message-events', methods=['POST'])
def welcomeRoot():
    data = request.get_json()
    message_id=data['data']['id']
    room_id=data['data']['roomId']
    sender_id=data['data']['roomId']
    person_id=data['data']['personId']

    app.logger.info(jsonify(request.json))
    app.logger.debug(f"got msg id: {message_id}")

    # Get message details
    messenger = Messenger()
    if app.debug == False:
        messenger.debug = False
    else:
        messenger.debug = True
    messenger.get_message(message_id)
    app.logger.info(f"got msg body: {messenger.message_text}")
    if messenger.message_text.startswith('/server '):
        try:
            action = messenger.message_text.split()[1]
        except IndexError:
            action = 'status'
        
        action_found = False

        if action == 'test':
            action_found = True
            app.logger.debug(f"action: {action}")
            messenger.send_message(room_id, f"performing action: {action}")
            
        if action == 'status':
            action_found = True
            app.logger.debug(f"action: {action}")
            messenger.send_message(room_id, f"performing action: {action}")

        if action == 'get_hostname':
            action_found = True
            app.logger.debug(f"action: {action}")
            msg_hostname = get_hostname(debug=messenger.debug)
            messenger.send_message(room_id, msg_hostname)
        
        if action == 'get_intf':
            action_found = True
            app.logger.debug(f"action: {action}")
            msg = get_interfaces(debug=messenger.debug)
            messenger.send_message(room_id, msg)

        if action == 'create_intf_portchannel':
            action_found = True
            app.logger.debug(f"action: {action}")
            try:
                interface_name = messenger.message_text.split()[2]
                interface_ip = messenger.message_text.split()[3]
                interface_mask = messenger.message_text.split()[4]
            except IndexError:
                interface_name = None
                interface_ip = None
                interface_mask = None
            msg = create_interface_via_device(debug=messenger.debug, interface_name=interface_name, interface_ip=interface_ip, interface_mask=interface_mask)
            messenger.send_message(room_id, msg)


        if action_found == False:
        # unknown action
            app.logger.debug(f"unknown action: {action}")
            messenger.send_message(room_id, f"Unknown action: {action}")

        return "Message processed"

    # Post our replay
    #ignore messages from myself
    if person_id == messenger.bot_id:
        app.logger.debug(f"ignore msg from myself")
        return "Message from myself are ignored"
    else:
        messenger.send_message(room_id, f"got message: {messenger.message_text}")

        # res = send_msg(TOKEN, data['data']['roomId'], str(dt.datetime.now()) + "\n" + message)
        # if res.status_code == 200:
        #         print("your message was successfully posted to Webex Teams")
        # else:
        #         print("failed with statusCode: %d" % res.status_code)
        #         if res.status_code == 404:
        #                 print ("please check the bot is in the room you're attempting to post to...")
        #         elif res.status_code == 400:
        #                 print ("please check the identifier of the room you're attempting to post to...")
        #         elif res.status_code == 401:
        #                 print ("please check if the access token is correct...")
    return "Message processed"

if __name__ == '__main__':
    if os.getenv('WEBEX_BOT_TOKEN') is None or os.getenv('WEBEX_BOT_TOKEN') == '':
        raise ValueError ("Please set the WEBEX_BOT_TOKEN environment variable")
    if os.getenv('DEBUG_NETOPS') is None or os.getenv('DEBUG_NETOPS') in ['False', 'false', '0', '']:
        app.logger.info(f"DEBUG_NETOPS: {os.getenv('DEBUG_NETOPS')}")
        app.debug = False
    else:
        app.debug = True
        app.logger.info(f"DEBUG_NETOPS: {os.getenv('DEBUG_NETOPS')}")
        app.logger.setLevel("DEBUG")
    app.run(host='0.0.0.0', port=8000)