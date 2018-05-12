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
info_text.append('/ibmqx4 - statistics for ibmqx4 quantum processor')
info_text.append('/ibmqx5 - statistics for ibmqx5 quantum processor')
info_text = '\n'.join(info_text)
counter = 0


def choose_backend(bot, update):
    global counter
    counter += 1

    update.message.reply_text('Wait a sec ...')

    backend = update.message.text[1:].lower()

    if backend in utils.backends:
        # create_statistics(backend)

        user_id = update.message.chat_id
        bot.send_photo(chat_id=user_id, photo=open('tmp/{}_to_send.png'.format(backend), 'rb'))
    else:
        help(bot, update)


def info(bot, update):
    update.message.reply_text(counter)


def help(bot, update):
    update.message.reply_text(info_text)


def main():
    updater = Updater(utils.get_token('res/token_telegram.json'))
    bot = telegram.Bot(token=utils.get_token('res/token_telegram.json'))
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
