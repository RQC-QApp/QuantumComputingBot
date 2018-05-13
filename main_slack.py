from flask import abort, Flask, jsonify, request
import concurrent.futures as cf
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
pool = cf.ThreadPoolExecutor(4)

extension_calibration = '_calibration_full.png'
extension_jobs = '_jobs_full.png'
extension_full = '_full.png'


###
# Slack API
###
@app.route('/confirm', methods=['POST'])
def confirm():
    req = request.form.to_dict()
    data = json.loads(req["payload"])
    backend = data["actions"][0]["name"]
    value = data["actions"][0]["value"]

    reply = None
    name = None
    if value.endswith(extension_jobs):
        name = 'Pending jobs for {}'.format(backend)
        reply = '*Pending jobs* for {} will be sent soon ...'.format(backend)
    elif value.endswith(extension_calibration):
        name = 'Calibration info for {}'.format(backend)
        reply = '*Calibration info* for {} will be sent soon ...'.format(backend)
    elif value.endswith(extension_full):
        name = 'Full statistics for {}'.format(backend)
        reply = '*Full statistics* for {} will be sent soon ...'.format(backend)

    if name is not None:
        pool.submit(send_image, 'tmp/{}'.format(value), name, data['channel']['id'])

    return reply


###
# Bot Commands
###
@app.route('/calibration', methods=['POST'])
def calibration():
    data = request.form.to_dict()
    backend = data['text'].lower()

    if backend in utils.backends:
        name = 'Calibration info for {}'.format(backend)
        pool.submit(send_image, 'tmp/{}{}'.format(backend, extension_calibration),
                    name, data['channel_id'])
        return "Wait a sec ..."
    else:
        send_buttons(data["response_url"], extension_calibration)
        return ''


@app.route('/jobs', methods=['POST'])
def jobs():
    data = request.form.to_dict()
    backend = data['text'].lower()

    if backend in utils.backends:
        name = 'Pending jobs for {}'.format(backend)
        pool.submit(send_image, 'tmp/{}{}'.format(backend, extension_jobs),
                    name, data['channel_id'])
        return "Wait a sec ..."
    else:
        send_buttons(data["response_url"], extension_jobs)
        return ''


@app.route('/full', methods=['POST'])
def full():
    data = request.form.to_dict()
    backend = data['text'].lower()

    if backend in utils.backends:
        name = 'Full statistics for {}'.format(backend)
        pool.submit(send_image, 'tmp/{}{}'.format(backend, extension_full),
                    name, data['channel_id'])
        return "Wait a sec ..."
    else:
        send_buttons(data["response_url"], extension_full)
        return ''


###
# Helper Functions
###
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
