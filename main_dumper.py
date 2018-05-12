from qiskit.backends import discover_local_backends, discover_remote_backends
from IBMQuantumExperience import IBMQuantumExperience
from slackclient import SlackClient
import json
import time
import pickle
import logging
import os
import utils

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

with open('res/token_q.json') as jsn:
    qx_config = json.load(jsn)
api = IBMQuantumExperience(token=qx_config['APItoken'], config={'url': qx_config['url']})


def dumper(delay):
    if os.path.exists(utils.PKL1) is False:
        data = list()
        with open(utils.PKL1, 'wb') as f:
            pickle.dump(data, f)
    if os.path.exists(utils.PKL2) is False:
        data = list()
        with open(utils.PKL2, 'wb') as f:
            pickle.dump(data, f)

    step = 0

    logger.info("Dumper is running!")
    while True:
        # Load.
        data = utils.load_data()

        # Append.
        # remote_backends = discover_remote_backends(api)
        remote_backends = utils.backends
        device_status = [api.backend_status(backend) for backend in remote_backends]

        data.append((time.time(), device_status))

        # Store.
        if step == 0:
            with open(utils.PKL1, 'wb') as f:
                pickle.dump(data, f)
        elif step == 1:
            with open(utils.PKL2, 'wb') as f:
                pickle.dump(data, f)

        step += 1
        step %= 2

        #############
        # Make Plots.
        for backend in utils.backends:
            utils.create_statistics(backend, api)
        ###

        # Sleep.
        time.sleep(delay)


def main():
    delay = 60  # Seconds.
    dumper(delay)


if __name__ == "__main__":
    main()
