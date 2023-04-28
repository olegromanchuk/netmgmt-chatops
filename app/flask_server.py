#!/usr/bin/env python3

from flask import Flask
from flask import jsonify
from flask import request
from messenger import Messenger
from restconf import Device
import datetime as dtc
import os
import sys

app = Flask(__name__)

@app.route('/hello/<string:name>', methods=['GET', 'POST'])
def welcome(name):
    return "Hello " + name

@app.route('/backup', methods=['GET', 'POST'])
def backupRoute():
    return "received request for backup"

@app.route('/message-events', methods=['POST'])
def welcomeRoot():
    app.logger.setLevel("DEBUG")
    data = request.get_json()
    message_id=data['data']['id']
    room_id=data['data']['roomId']
    sender_id=data['data']['roomId']
    person_id=data['data']['personId']

    app.logger.info(jsonify(request.json))
    app.logger.debug(f"got msg id: {message_id}")

    # Get message details
    messenger = Messenger()
    messenger.get_message(message_id)
    app.logger.info(f"got msg body: {messenger.message_text}")
    if messenger.message_text.startswith('/server'):
        try:
            action = messenger.message_text.split()[1]
        except IndexError:
            action: 'status'

        if action == 'start':
            app.logger.debug(f"action: start")
            messenger.send_message(room_id, f"performing action: {action}")

        elif action == 'stop':
            app.logger.debug(f"action: stop")
            messenger.send_message(room_id, f"performing action: {action}")

        elif action == 'get_hostname':
            app.logger.debug(f"action: get_hostname")
            device = Device()
            try:
                hostname = device.get_hostname()
                messenger.send_message(room_id, f"hostname: {hostname}")
            except Exception as e:
                app.logger.error(f"Error: 7001 failed to get hostname. Error: {e}")
                messenger.send_message(room_id, f"Error: 7001. Mgs: failed to get hostname: cannot connect to device")
        else:
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
    app.run(host='0.0.0.0', port=8000)