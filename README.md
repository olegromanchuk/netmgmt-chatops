IOS XE version 16.9 - Fuji


# How to use
1. export ${BOT_TOKEN} (check the file .env)
2. Run ngrok: `ngrok http 8000`
3. Paste url from ngrok (https://69f4-100-2-209-180.ngrok.io) into postman "Webex -> Update webhook -> targetUrl"  
NOTE: update only base url. Leave /message-events  
Or use the curl below. Replace "targetUrl" with the ngrok url from above.
```
curl --location --request PUT 'https://webexapis.com/v1/webhooks/Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1dFQkhPT0svNzlmN2Y4ZjYtZTBiNy00ZTI4LTlmZWYtMGQ3YTRlNTkyMGM3' \
--header "Authorization: Bearer ${BOT_TOKEN}" \
--header 'Content-Type: application/json' \
--data-raw '{
  "name": "webhookNetMgmt",
  "targetUrl": "https://feba-100-2-209-180.ngrok.io/message-events"
}'
```
4. start the app: `./flask_server.py`


## Install

1. Setup env
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

2. Create webhook (if needed)
```
curl --location --request POST 'https://webexapis.com/v1/webhooks' \
--header "Authorization: Bearer ${BOT_TOKEN}" \
--header 'Content-Type: application/json' \
--data-raw '{
  "name": "webhookNetMgmt",
  "targetUrl": "https://42ad-100-2-209-180.ngrok.io/message-events",
  "resource": "messages",
  "event": "created"
}'
``` 


## Debug in Visual Studio Code

Open the ChatOps code samples in VSCode, make sure you have the Python extension is installed.

```shell
> git clone https://github.com/CiscoDevNet/devnet-express-cloud-collab-code-samples
> cd devnet-express-cloud-collab-code-samples
> cd itp
> cd collab-spark-chatops-bot-itp
> code .
```

Then, in VS Code, open .vscode/launch.json file, and replace the values as mentionned:

```json
            "args": [
                "-r",
                "PASTE THE IDENTIFIER OF THE ROOM YOU ADDED YOUR BOT TO",
                "-m",
                "customize this chatops message"
            ],
            "env": {
                "SPARK_ACCESS_TOKEN" : "PASTE YOUR BOT ACCESS TOKEN HERE"
            }
```

Now, select the chatops.py 
and hit F5 to run the "ChatOps" launch configuration, or by clicking the ChatOps Debug configuration.

