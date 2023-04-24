#!/usr/bin/env python

from flask import Flask
from flask import jsonify
from flask import request
from messenger import Messenger
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
    app.logger.info(f"got msg id: {message_id}")

    # Get message details
    messenger = Messenger()
    messenger.get_message(message_id)
    app.logger.info(f"got msg body: {messenger.message_text}")
    if messenger.message_text.startswith('/server'):
        try:
            action = messenger.message_text.split()[1]
        except IndexError:
            action: 'status'
        messenger.send_message(room_id, f"performing action: {action}")
        return

    # Post our replay
    #ignore messages from myself
    if person_id == messenger.bot_id:
        app.logger.info(f"ignore msg from myself")
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
    return

if __name__ == '__main__':
    if os.getenv('BOT_TOKEN') is None:
        print("Please set the BOT_TOKEN environment variable")
        sys.exit(1)
    app.run(host='0.0.0.0', port=8000)