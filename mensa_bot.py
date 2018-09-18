import logging

from telegram.ext import Updater, CommandHandler

from mensa_parser import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start(bot, update, job_queue):
    message = "Hey, I will send the menu every weekday at 10:00."
    bot.send_message(chat_id=update.message.chat_id, text=message)
    job_queue.run_daily(daily_menu, datetime.time(10, 0), days=(0, 1, 2, 3, 4),
                        context=update.message.chat_id)


def stop(bot, update, job_queue):
    jobs = job_queue.get_jobs_by_name(update.message.chat_id)
    bot.send_message(chat_id=update.message.chat_id,
                     text="I will stop sending the menu to this chat    .".format(update.message.chat_id))
    for cur_job in jobs:
        cur_job.schedule_removal()


def menu(bot, update, args):
    message = ""
    listed_mensas = list(set(args))

    if len(listed_mensas) == 0:
        message = get_menu(Mensa.DEFAULT)
    else:
        for i, cur_mensa_arg in enumerate(listed_mensas):
            cur_mensa = Mensa.from_string(cur_mensa_arg)
            if not cur_mensa == Mensa.UNKNOWN:
                message += get_menu(cur_mensa)
            else:
                message += "Entschuldige, die Mensa '{}' ist mir nicht bekannt.".format(listed_mensas[i])

            if i < len(listed_mensas):
                message += '\n\n'

    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode='Markdown')


def daily_menu(bot, job):
    if job.context:
        message = get_menu_as_string(Mensa.DEFAULT)
        bot.send_message(chat_id=job.context, text=message, parse_mode='Markdown')
    else:
        print("Error!")


def get_token():
    with open('token_testbot') as token_file:
        return token_file.readline()


class MensaBot:

    def __init__(self):
        self.updater = Updater(token=get_token())
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue

        self.add_handler()
        self.start()
        print("Bot started.")

    def start(self):
        self.updater.start_polling()

    def add_handler(self):
        start_handler = CommandHandler('start', start, pass_job_queue=True)
        stop_handler = CommandHandler('stop', stop, pass_job_queue=True)
        menu_handler = CommandHandler('menu', menu, pass_args=True)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(stop_handler)
        self.dispatcher.add_handler(menu_handler)
