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
  "targetUrl": "https://e1a3-100-2-209-180.ngrok-free.app/message-events"
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
  "targetUrl": "https://9554-100-2-209-180.ngrok-free.app/message-events",
  "resource": "messages",
  "event": "created"
}'
``` 


## Docker version
IMAGE_VERSION=netmgmtchatops:version1.0
docker build -t ${IMAGE_VERSION} .
docker run -p 8000:8000 -e BOT_TOKEN=${BOT_TOKEN} --name netmgmtchatops ${IMAGE_VERSION}


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


## Restconf for local development
Works starting from IOS XE version 16.06
# Next line will forward traffic on bastion host 8443->443 to cisco.with.ios-xe.restconf.host
# same as iptables -t nat -A PREROUTING -p tcp --dport 8443 -j DNAT --to-destination 192.168.1.100:443

``sudo ssh -L 8443:cisco.with.ios-xe.restconf.host:443 root@bastion.host -N``
```
The SSH command will establish a connection to the bastion host and forward the specified local port to the target machine. You may be prompted to enter the password or use a private key for authentication.

Now, you can access the target machine on the forwarded port using localhost and the specified local port. For example, if you forwarded an HTTP service on port 80, you can access it in your browser using the address http://localhost:8080.
```


