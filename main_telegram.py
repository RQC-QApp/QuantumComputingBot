from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import logging
import json
import utils

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - \
                            %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

info_text = []
info_text.append('You can control me by sending these commands:')
info_text.append('')
info_text.append('/gate_errors_ibmqx4 - send gate errors')
info_text.append('/readout_errors_ibmqx4 - send readout errors')
info_text.append('/jobs_ibmqx4 - diagram of pending jobs')
info_text.append('/full_ibmqx4 - calibration and pending jobs info')
info_text.append('')
info_text.append('/gate_errors_ibmqx5 - send gate errors')
info_text.append('/readout_errors_ibmqx5 - send readout errors')
info_text.append('/jobs_ibmqx5 - diagram of pending jobs')
info_text.append('/full_ibmqx5 - calibration and pending jobs info')
info_text = '\n'.join(info_text)
counter = 0


def choose_backend(bot, update):
    global counter
    counter += 1

    update.message.reply_text('Wait a sec ...')
    user_id = update.message.chat_id

    command = update.message.text.lower()
    path = None
    if command == '/gate_errors_ibmqx4':
        path = 'tmp/ibmqx4_gateerrors_full.png'
    elif command == '/readout_errors_ibmqx4':
        path = 'tmp/ibmqx4_readouterrors_full.png'
    elif command == '/jobs_ibmqx4':
        path = 'tmp/ibmqx4_jobs_full.png'
    elif command == '/full_ibmqx4':
        path = 'tmp/ibmqx4_full.png'
    elif command == '/gate_errors_ibmqx5':
        path = 'tmp/ibmqx5_gateerrors_full.png'
    elif command == '/readout_errors_ibmqx5':
        path = 'tmp/ibmqx5_readouterrors_full.png'
    elif command == '/jobs_ibmqx5':
        path = 'tmp/ibmqx5_jobs_full.png'
    elif command == '/full_ibmqx5':
        path = 'tmp/ibmqx5_full.png'

    if path is None:
        help(bot, update)
    else:
        bot.send_photo(chat_id=user_id, photo=open(path, 'rb'))
    return


def info(bot, update):
    update.message.reply_text(counter)
    return


def help(bot, update):
    update.message.reply_text(info_text)
    return


def main():
    print('-> USE PROXY')

    token = utils.get_token('res/token_telegram.json')
    req = telegram.utils.request.Request(proxy_url='socks5://127.0.0.1:9050',
                                         read_timeout=30, connect_timeout=20,
                                         con_pool_size=10)
    bot = telegram.Bot(token=token, request=req)
    updater = Updater(bot=bot)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('info', info))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('start', help))
    dp.add_handler(MessageHandler(Filters.command, choose_backend))
    dp.add_handler(MessageHandler(Filters.text, help))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
