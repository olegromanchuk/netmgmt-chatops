import json
import requests
import requests.utils
import os
from urllib.parse import urlparse, parse_qs
from pprint import pprint

TOKEN=os.getenv('WEBEX_BOT_TOKEN')

BASE_URL = "https://webexapis.com/v1"

max_items=3
room_id=''

class Messenger():
    def __init__(self, base_url=BASE_URL, api_key=TOKEN):
        self.base_url=base_url
        self.api_key=api_key
        self.max_items=max_items
        self.room_id=room_id
        self.headers = {
            'Authorization': 'Bearer ' + TOKEN,
            'Content-Type': 'application/json'
        }
        self.bot_id=requests.get(f'{base_url}/people/me', headers=self.headers).json().get('id')

    def get_message(self, message_id):
        received_message_url=f'{self.base_url}/messages/{message_id}'
        # app.logger.debug(f"sending msg to: {received_message_url}")
        self.message_text=requests.get(received_message_url, headers=self.headers).json().get('text')

    
    def send_message(self, room_id, message):
            message_url=f'{self.base_url}/messages'
            data = {"roomId": room_id,
                    "text": message}
            return requests.post(message_url, headers=self.headers, data=json.dumps(data), verify=True).json

    def get_message(self, message_id):
        received_message_url=f'{self.base_url}/messages/{message_id}'
        # app.logger.debug(f"sending msg to: {received_message_url}")
        self.message_text=requests.get(received_message_url, headers=self.headers).json().get('text')

    def _get_parsed_link_headers(self):
        link_header={}
        link_header["rel"]=requests.utils.parse_header_links(self.response.headers["Link"])[0]["rel"]
        