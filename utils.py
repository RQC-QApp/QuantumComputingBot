from datetime import date, timedelta
from datetime import datetime as dt
from matplotlib.font_manager import findfont, FontProperties
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import requests
import threading
import pickle
import time
import json
import math
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


PKL1 = 'data/real_data_1.pkl'
PKL2 = 'data/real_data_2.pkl'

backends = ['ibmqx4', 'ibmqx5']


def get_token(path):
    with open(path) as jsn:
        data = json.load(jsn)
    return data['token']


def load_data():
    data = None
    try:
        with open(PKL1, 'rb') as f:
            data = pickle.load(f)
    except (pickle.UnpicklingError, EOFError) as e:
        with open(PKL2, 'rb') as f:
            data = pickle.load(f)
    return data


def plot_pending_jobs(backend):
    data = load_data()

    times = sorted([x[0] for x in data])
    pending_jobs = [[y for y in x[1] if y['backend'] == backend][0]['pending_jobs']
                    for x in sorted(data, key=lambda x: x[0])]

    ###
    # Jobs Full.
    plt.close()
    plt.figure(figsize=(11, 5))
    plt.grid(True, zorder=5)
    plt.fill_between(times, pending_jobs, color='brown')
    plt.locator_params(axis='x', nbins=11)
    # New xticks.
    locs, labels = plt.xticks()
    new_ticks = [dt.fromtimestamp(x).strftime('%H:%M') for x in locs]
    plt.xticks(locs[1:-1], new_ticks[1:-1], rotation=0, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylim(0, math.ceil(max(pending_jobs)) + 1)
    plt.title('IBMQ Backend: {},\nLocal time of bot: {}'.format(backend,
              dt.fromtimestamp(time.time()).strftime('%Y, %b %d, %H:%M')), fontsize=15)
    plt.xlabel('Time', fontsize=15)
    plt.ylabel('# of pending jobs', fontsize=15)
    plt.savefig('tmp/{}_jobs_full.png'.format(backend), bbox_inches='tight')
    plt.close()

    img_jobs = Image.open('tmp/{}_jobs_full.png'.format(backend), 'r')
    img_jobs_w, img_jobs_h = img_jobs.size
    img_background = Image.new('RGBA', (img_jobs_w, img_jobs_h),
                               (255, 255, 255, 255))
    img_background_w, img_background_h = img_background.size

    #############
    # Load Logos.
    img_qiskit = Image.open('res/qiskit-logo.png', 'r')
    factor = 7
    img_qiskit = img_qiskit.resize((img_qiskit.size[0] // factor, img_qiskit.size[1] // factor))
    img_qiskit_w, img_qiskit_h = img_qiskit.size

    img_rqc = Image.open('res/rqc.jpg', 'r')
    factor = 13
    img_rqc = img_rqc.resize((img_rqc.size[0] // factor, img_rqc.size[1] // factor))
    img_rqc_w, img_rqc_h = img_rqc.size
    ####

    ########
    # Paste.
    offset = (0, 0)
    img_background.paste(img_jobs, offset)

    displacement_h = 8
    displacement_w = 10
    offset = (img_background_w - img_qiskit_w - displacement_w, displacement_h - 4)
    img_background.paste(img_qiskit, offset)

    offset = (img_background_w - img_rqc_w - img_qiskit_w - displacement_w - 7, displacement_h)
    img_background.paste(img_rqc, offset)
    img_background.save('tmp/{}_jobs_full.png'.format(backend))
    img_background.close()
    img_rqc.close()
    img_jobs.close()

    ###
    # Jobs Part.
    plt.close()
    plt.figure(figsize=(11, 5))
    plt.grid(True, zorder=5)
    plt.fill_between(times, pending_jobs, color='brown')
    plt.locator_params(axis='x', nbins=11)
    # New xticks.
    locs, labels = plt.xticks()
    new_ticks = [dt.fromtimestamp(x).strftime('%H:%M') for x in locs]
    plt.xticks(locs[1:-1], new_ticks[1:-1], rotation=0, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylim(0, math.ceil(max(pending_jobs)) + 1)
    plt.title('Local time of bot: {}'.format(dt.fromtimestamp(time.time()).strftime('%Y, %b %d, %H:%M')),
              fontsize=15)
    plt.xlabel('Time', fontsize=15)
    plt.ylabel('# of pending jobs', fontsize=15)
    plt.savefig('tmp/{}_jobs_part.png'.format(backend), bbox_inches='tight')
    plt.close()
    return


def plot_readout_errors(backend, api):
    try:
        full_info = api.backend_calibration(backend=backend)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return
    except Exception as e:
        print(e)
        return

    N_qubits = len(full_info['qubits'])
    qubits = [full_info['qubits'][qub]['name'] for qub in range(N_qubits)]
    readout_error = [full_info['qubits'][qub]['readoutError']['value'] for qub in range(N_qubits)]
    readout_error = np.array([readout_error])

    readout_error *= 100

    last_update = full_info['lastUpdateDate']
    last_update = dt.strptime(last_update, "%Y-%m-%dT%H:%M:%S.000Z").timestamp()
    last_update = dt.fromtimestamp(last_update).strftime('%Y, %b %d, %H:%M')

    ###
    # Readout Errors Full.
    plt.close()
    plt.figure(figsize=(15, 15))
    plt.matshow(readout_error, cmap='Reds', fignum=1)
    # Placing actual values in the matshow plot
    for (i,), value in np.ndenumerate(readout_error[0]):
        plt.text(i, 0, '{:0.2f}'.format(value), ha='center', va='center')

    # Formatting axes.
    plt.xticks(np.arange(N_qubits), qubits)
    plt.yticks([], [])
    plt.autoscale(axis='both', tight=True)

    plt.title('IBMQ Backend: {}, Readout errors,\nLast calibration: {}\n'.format(backend, last_update), fontsize=15)
    plt.margins(tight=True)
    plt.savefig('tmp/{}_readouterrors_full.png'.format(backend), bbox_inches='tight')
    plt.close()

    img_rerr = Image.open('tmp/{}_readouterrors_full.png'.format(backend), 'r')
    img_rerr_w, img_rerr_h = img_rerr.size
    img_background = Image.new('RGBA', (img_rerr_w, img_rerr_h),
                               (255, 255, 255, 255))
    img_background_w, img_background_h = img_background.size

    #############
    # Load Logos.
    img_qiskit = Image.open('res/qiskit-logo.png', 'r')
    factor = 7
    img_qiskit = img_qiskit.resize((img_qiskit.size[0] // factor, img_qiskit.size[1] // factor))
    img_qiskit_w, img_qiskit_h = img_qiskit.size

    img_rqc = Image.open('res/rqc.jpg', 'r')
    factor = 14
    img_rqc = img_rqc.resize((img_rqc.size[0] // factor, img_rqc.size[1] // factor))
    img_rqc_w, img_rqc_h = img_rqc.size
    ####

    #######
    # Paste.
    offset = (0, 0)
    img_background.paste(img_rerr, offset)

    displacement_h = 8
    displacement_w = 10
    offset = (img_background_w - img_qiskit_w - displacement_w, displacement_h - 4)
    img_background.paste(img_qiskit, offset)

    offset = (img_background_w - img_rqc_w - img_qiskit_w - displacement_w - 7, displacement_h)
    img_background.paste(img_rqc, offset)

    img_background.save('tmp/{}_readouterrors_full.png'.format(backend))
    img_background.close()
    img_rqc.close()
    img_rerr.close()

    ###
    # Readout Errors Part.
    plt.close()
    plt.figure(figsize=(15, 15))
    plt.matshow(readout_error, cmap='Reds', fignum=1)
    # Placing actual values in the matshow plot
    for (i,), value in np.ndenumerate(readout_error[0]):
        plt.text(i, 0, '{:0.2f}'.format(value), ha='center', va='center', fontsize=16)

    # Formatting axes.
    plt.xticks(np.arange(N_qubits), qubits, fontsize=16)
    plt.yticks([], [])
    plt.autoscale(axis='both', tight=True)

    plt.title('IBMQ Backend: {}\nLast calibration: {}\n\nReadout errors\n'.format(backend, last_update), fontsize=20)
    plt.margins(tight=True)
    plt.savefig('tmp/{}_readouterrors_part.png'.format(backend), bbox_inches='tight')
    plt.close()
    return


def plot_gate_errors(backend, api):
    try:
        full_info = api.backend_calibration(backend=backend)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return
    except Exception as e:
        print(e)
        return

    # Info.
    N_qubits = len(full_info['qubits'])
    qubits = [full_info['qubits'][qub]['name'] for qub in range(N_qubits)]
    gate_error = [full_info['qubits'][qub]['gateError']['value'] for qub in range(N_qubits)]
    gate_error = np.array([gate_error])
    full_info = api.backend_calibration(backend=backend)
    last_update = full_info['lastUpdateDate']
    last_update = dt.strptime(last_update, "%Y-%m-%dT%H:%M:%S.000Z").timestamp()
    last_update = dt.fromtimestamp(last_update).strftime('%Y, %b %d, %H:%M')

    #####
    # Multiqubit error.
    multi_qubit_gates = [full_info['multiQubitGates'][qub]['qubits'] for qub in range(N_qubits)]
    multi_qubit_error = np.array([full_info['multiQubitGates'][qub]['gateError']['value'] for qub in range(N_qubits)])

    multi_qubit_error *= 100
    gate_error *= 100

    # creating gate error matrix.
    error_matrix = np.zeros((N_qubits, N_qubits))

    error_matrix[:, :] = None
    for i in range(len(multi_qubit_gates)):
        gate = multi_qubit_gates[i]
        qub1, qub2 = gate[0], gate[1]
        error_matrix[qub1][qub2] = multi_qubit_error[i]
        error_matrix[qub2][qub1] = multi_qubit_error[i]
        error_matrix[i][i] = gate_error[0][i]

    fontsize = None
    if backend == 'ibmqx4':
        fontsize = 13
    elif backend == 'ibmqx5':
        fontsize = 8

    ###
    # Gate Errors Full.
    plt.close()
    plt.figure(figsize=(7, 7))
    plt.matshow(error_matrix, cmap='Reds', fignum=1)
    plt.title('IBMQ Backend: {},\nQubit gate errors,\nLast calibration: {}'.format(backend, last_update), fontsize=15)
    # Placing actual values in the matshow plot
    for (i, j), value in np.ndenumerate(error_matrix):
        if not np.isnan(value):
            plt.text(j, i, '{:0.2f}'.format(value), ha='center', va='center', fontsize=fontsize)
    # Formatting axes
    plt.yticks(np.arange(N_qubits), qubits)
    plt.xticks(np.arange(N_qubits), qubits)
    plt.autoscale(axis='both', tight=True)
    plt.savefig('tmp/{}_gateerrors_full.png'.format(backend), bbox_inches='tight')
    plt.close()

    img_gerr = Image.open('tmp/{}_gateerrors_full.png'.format(backend), 'r')
    img_gerr_w, img_gerr_h = img_gerr.size
    img_background = Image.new('RGBA', (img_gerr_w, img_gerr_h),
                               (255, 255, 255, 255))
    img_background_w, img_background_h = img_background.size

    #############
    # Load Logos.
    img_qiskit = Image.open('res/qiskit-logo.png', 'r')
    factor = 7
    img_qiskit = img_qiskit.resize((img_qiskit.size[0] // factor, img_qiskit.size[1] // factor))
    img_qiskit_w, img_qiskit_h = img_qiskit.size

    img_rqc = Image.open('res/rqc.jpg', 'r')
    factor = 14
    img_rqc = img_rqc.resize((img_rqc.size[0] // factor, img_rqc.size[1] // factor))
    img_rqc_w, img_rqc_h = img_rqc.size
    ####

    #######
    # Paste.
    offset = (0, 0)
    img_background.paste(img_gerr, offset)

    displacement_h = 5
    displacement_w = 5
    offset = (displacement_w, img_rqc_h + displacement_h)
    img_background.paste(img_qiskit, offset)

    offset = (displacement_w, displacement_h)
    img_background.paste(img_rqc, offset)
    img_background.save('tmp/{}_gateerrors_full.png'.format(backend))
    img_background.close()
    img_rqc.close()
    img_gerr.close()
    ###

    ###
    # Gate Errors Part.
    plt.close()
    plt.figure(figsize=(6, 6))
    plt.matshow(error_matrix, cmap='Reds', fignum=1)
    plt.title('Qubit gate errors', fontsize=15)
    # Placing actual values in the matshow plot
    for (i, j), value in np.ndenumerate(error_matrix):
        if not np.isnan(value):
            plt.text(j, i, '{:0.2f}'.format(value), ha='center', va='center', fontsize=fontsize)
    # Formatting axes
    plt.yticks(np.arange(N_qubits), qubits)
    plt.xticks(np.arange(N_qubits), qubits)
    plt.autoscale(axis='both', tight=True)
    plt.savefig('tmp/{}_gateerrors_part.png'.format(backend), bbox_inches='tight')
    plt.close()


def plot_full(backend, api):
    plot_gate_errors(backend, api)
    plot_readout_errors(backend, api)
    plot_pending_jobs(backend)

    img_gerr = Image.open('tmp/{}_gateerrors_part.png'.format(backend), 'r')
    img_gerr_w, img_gerr_h = img_gerr.size

    img_rerr = Image.open('tmp/{}_readouterrors_part.png'.format(backend), 'r')
    img_rerr_w, img_rerr_h = img_rerr.size

    img_jobs = Image.open('tmp/{}_jobs_part.png'.format(backend), 'r')
    img_jobs_w, img_jobs_h = img_jobs.size

    img_background = Image.new('RGBA', (img_gerr_w + img_jobs_w, img_rerr_h + img_gerr_h),
                               (255, 255, 255, 255))
    img_background_w, img_background_h = img_background.size

    #############
    # Load Logos.
    img_qiskit = Image.open('res/qiskit-logo.png', 'r')
    factor = 4
    img_qiskit = img_qiskit.resize((img_qiskit.size[0] // factor, img_qiskit.size[1] // factor))
    img_qiskit_w, img_qiskit_h = img_qiskit.size

    img_rqc = Image.open('res/rqc.jpg', 'r')
    factor = 7
    img_rqc = img_rqc.resize((img_rqc.size[0] // factor, img_rqc.size[1] // factor))
    img_rqc_w, img_rqc_h = img_rqc.size
    ####

    ##############
    # Paste Plots.
    offset = ((img_background_w - img_rerr_w) // 2, 0)
    img_background.paste(img_rerr, offset)

    offset = (0, img_rerr_h)
    img_background.paste(img_gerr, offset)

    offset = (img_gerr_w, (img_rerr_h + img_background_h - img_jobs_h) // 2)
    img_background.paste(img_jobs, offset)
    ####

    ##############
    # Paste Logos.
    displacement_h = 8
    displacement_w = 10
    offset = (img_background_w - img_qiskit_w - displacement_w, displacement_h - 6)
    img_background.paste(img_qiskit, offset)

    offset = (img_background_w - img_rqc_w - img_qiskit_w - displacement_w - 7, displacement_h)
    img_background.paste(img_rqc, offset)
    ###

    img_background.save('tmp/{}_full.png'.format(backend))

    img_background.close()
    img_rqc.close()
    img_gerr.close()
    img_rerr.close()
    img_jobs.close()


if __name__ == '__main__':
    raise RuntimeError
