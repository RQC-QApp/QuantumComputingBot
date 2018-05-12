from slackclient import SlackClient
import logging
import json
import time
import os
import utils

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

slack_client = SlackClient(utils.get_token('res/token_slack.json'))
starterbot_id = None

# Constants.
RTM_READ_DELAY = 0.1  # 1 second delay between reading from RTM.
counter = 0


def parse_bot_commands(slack_events):
    for event in slack_events:
        if event["type"] == "message" and "subtype" not in event:
            message = event["text"]
            return message, event["channel"]
    return None, None


def handle_command(command, channel):
    global counter
    backend = command.lower()

    if backend in utils.backends:
        counter += 1
        response = "Wait a sec ..."
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )
        # utils.create_statistics(backend)
        slack_client.api_call(
            'files.upload',
            channels=channel,
            as_user=True,
            filename=backend,
            file=open('tmp/{}_to_send.png'.format(backend), 'rb'),
        )
    elif command == 'info':
        response = str(counter)
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )
    else:
        response = list()
        response.append("I'm sorry, I don't understand!")
        response.append("I understand only these messages: *ibmqx4* or *ibmqx5*")
        response = '\n'.join(response)
        slack_client.api_call(
            "chat.postMessage",
            channel=channel,
            text=response
        )


def main():
    if slack_client.rtm_connect(with_team_state=False):
        # Read bot's user ID by calling Web API method `auth.test`.
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        logger.info("Bot is connected and running!")

        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        logger.info("Connection failed. Exception traceback printed above.")


if __name__ == "__main__":
    main()
