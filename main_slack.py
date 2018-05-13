from flask import abort, Flask, jsonify, request
import requests
import logging
import utils
import json
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
app = Flask(__name__)

slack_token = utils.get_token('res/token_slack.json')


###
# Slack API
###

@app.route('/confirm', methods=['POST'])
def confirm():
    req = request.form.to_dict()
    data = json.loads(req["payload"])
    backend = data["actions"][0]["name"]
    value = data["actions"][0]["value"]

    payload = {
        "text": "Ok :slightly_smiling_face:",
    }
    headers = {
        'content-type': "application/json",
    }
    response = requests.request("POST", data['response_url'], data=json.dumps(payload), headers=headers)
    print(response.text)

    send_image('tmp/{}'.format(value), backend, data['channel']['id'])

    return ""


###
# Bot Commands
###
@app.route('/calibration', methods=['POST'])
def calibration():
    data = request.form.to_dict()
    backend = data['text'].lower()

    extension = '_multiqubut_err.png'

    if backend in utils.backends:
        quick_response(data['response_url'])
        send_image('tmp/{}{}'.format(backend, extension), backend, data['channel_id'])
    else:
        send_buttons(data["response_url"], extension)

    return ""


@app.route('/jobs', methods=['POST'])
def jobs():
    data = request.form.to_dict()
    backend = data['text'].lower()

    extension = '.png'

    if backend in utils.backends:
        quick_response(data['response_url'])
        send_image('tmp/{}{}'.format(backend, extension), backend, data['channel_id'])
    else:
        send_buttons(data["response_url"], extension)

    return ""


@app.route('/full', methods=['POST'])
def full():
    data = request.form.to_dict()
    backend = data['text'].lower()

    extension = '_to_send.png'

    if backend in utils.backends:
        quick_response(data['response_url'])
        send_image('tmp/{}{}'.format(backend, extension), backend, data['channel_id'])
    else:
        send_buttons(data["response_url"], extension)

    return ""


###
# Helper Functions
###
def quick_response(response_url):
    payload = {
        "text": "Wait a sec :hourglass_flowing_sand:",
    }
    headers = {
        'content-type': "application/json",
    }
    response = requests.request("POST", response_url, data=json.dumps(payload), headers=headers)
    print(response.text)


def send_image(path, name, channel):
    my_file = {
        'file': (path, open(path, 'rb'), 'png')
    }
    payload = {
        "filename": name,
        'token': slack_token,
        "channels": [channel]
    }

    response = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)


def send_buttons(response_url, extension):
    payload = {
        "text": "What backend you are interested in?",
        "attachments": [
            {
                "text": "Choose a backend :qiskit:",
                "callback_id": 42,
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "ibmqx4",
                        "text": "ibmqx4",
                        "type": "button",
                        "value": "ibmqx4{}".format(extension)
                    },
                    {
                        "name": "ibmqx5",
                        "text": "ibmqx5",
                        "type": "button",
                        "value": "ibmqx5{}".format(extension)
                    },
                ]
            }
        ]
    }

    headers = {
        'content-type': "application/json",
    }

    response = requests.request("POST", response_url, data=json.dumps(payload), headers=headers)
    print(response.text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
