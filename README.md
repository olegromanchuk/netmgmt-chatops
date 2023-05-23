# Netchatops
Network management chatops connects [webex](https://www.webex.com) chat (frontend) with the restconf scripts that accepts commands from chat and sends them to devices (backend).

## Getting Started

First, you need to create a webex bot application. Webex is free. Create an account on [webex](https://www.webex.com) and follow instructions on the [developer.webex.com](https://developer.webex.com/) to create a bot.

Second, you need to have a device that supports restconf. Cisco IOS XE supports restconf from version 16.06. Note, that redundancy SSO on ASR is currently not supported along with restconf (at least on 16.X).


## How to configure a webhook for webex bot
If you already configured bot you can skip this part.

### Run in test mode via ngrok on local machine
1. export ${WEBEX_BOT_TOKEN} (check the file .env_example)
2. Run ngrok: `ngrok http 8000`
3. Paste url from ngrok (https://69f4-100-2-209-180.ngrok.io) into curl below. Replace "targetUrl" with the ngrok url from above. Replace webhookID on actual webhookID that you created. 
```
curl --location --request PUT 'https://webexapis.com/v1/webhooks/Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1dFQkhPT0svNzlmN2Y4ZjYtZTBiNy00ZTI4LTlmZWYtMGQ3YTRlNTkyMGM3' \
--header "Authorization: Bearer ${WEBEX_BOT_TOKEN}" \
--header 'Content-Type: application/json' \
--data-raw '{
  "name": "webhookNetMgmt",
  "targetUrl": "https://ce55-100-2-209-180.ngrok-free.app/message-events"
}'
```

4. Set env variables for app
``` 
export WEBEX_BOT_TOKEN='myToken'
export RESTCONF_USERNAME='myRestConfDeviceName'
export RESTCONF_PASSWORD='myRestConfDevicePass'
export DEVICE_IP_PORT='deviceIP:port'
```

From this point you can run app locally or in docker. Both options uses env variables from the step 4.


### Run in docker
```
docker run -p 8000:8000 -e WEBEX_BOT_TOKEN=${WEBEX_BOT_TOKEN} -e RESTCONF_USERNAME=${RESTCONF_USERNAME} -e RESTCONF_PASSWORD=${RESTCONF_PASSWORD} -e DEVICE_IP_PORT=${DEVICE_IP_PORT} --name netmgmtchatops kravetc/netmgmtchatops
```

### Run locally
1. Setup env
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

2. Run the app
```
start the app: `./flask_server.py`
```

## Available links

* /hello world (test)
* /server status (dummy)
* /server get_intf
* /server get_hostname
* /server create_intf_portchannel 16 172.16.16.5 255.255.255.0



# Development

### Prepare local development environment
1. [Setup env variables](#run-locally)

2. [Create webhook (if needed)](#run-in-test-mode-via-ngrok-on-local-machine)


### How to build and run docker version
```
IMAGE_VERSION=netmgmtchatops:version1.0
docker build -t ${IMAGE_VERSION} .
docker run -p 8000:8000 -e WEBEX_BOT_TOKEN=${WEBEX_BOT_TOKEN} -e RESTCONF_USERNAME=${RESTCONF_USERNAME} -e RESTCONF_PASSWORD=${RESTCONF_PASSWORD} --name netmgmtchatops ${IMAGE_VERSION}
```


### Debug in Visual Studio Code
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
Restconf works starting from IOS XE version 16.06  
Next line will forward traffic on bastion host 8443 -> cisco.with.ios-xe.restconf.host:433  
Same as `iptables -t nat -A PREROUTING -p tcp --dport 8443 -j DNAT --to-destination 192.168.1.100:443`

```
sudo ssh -L 8443:cisco.with.ios-xe.restconf.host:443 root@bastion.host -N
```
The SSH command will establish a connection to the bastion host and forward the specified local port to the target machine. You may be prompted to enter the password or use a private key for authentication.

Now, you can access the target machine on the forwarded port using localhost and the specified local port. For example, if you forwarded an HTTP service on port 80, you can access it in your browser using the address http://localhost:8080.
