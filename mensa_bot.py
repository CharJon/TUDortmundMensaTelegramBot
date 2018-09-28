import logging

from telegram.ext import Updater, CommandHandler

from mensa_parser import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def get_token_from_file():
    with open('token_testbot') as token_file:
        return token_file.readline()


class MensaBot:

    def __init__(self):
        self.updater = Updater(token=get_token_from_file())
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue

        self.add_handler()
        self.start_bot()
        print("Bot started.")

    def start_bot(self):
        self.add_jobs_from_db_to_queue()
        self.updater.start_polling()

    def add_handler(self):
        start_handler = CommandHandler('start', self.start)
        stop_handler = CommandHandler('stop', self.stop, pass_job_queue=True)
        menu_handler = CommandHandler('menu', self.menu, pass_args=True)
        status_handler = CommandHandler('status', self.status, pass_job_queue=True)
        start_daily_handler = CommandHandler('start_daily', self.start_daily, pass_job_queue=True)
        stop_daily_handler = CommandHandler('stop_daily', self.stop_daily, pass_job_queue=True)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(stop_handler)
        self.dispatcher.add_handler(menu_handler)
        self.dispatcher.add_handler(status_handler)
        self.dispatcher.add_handler(start_daily_handler)
        self.dispatcher.add_handler(stop_daily_handler)

    def add_jobs_from_db_to_queue(self):
        pass

    def start(self, bot, update):
        message = "Hey :)" + '\n' + "Über /menu schicke ich das aktuelle Menü der Mensa-Nord."
        bot.send_message(chat_id=update.message.chat_id, text=message)

    def stop(self, bot, update, job_queue):
        jobs = job_queue.get_jobs_by_name(update.message.chat_id)

        message = "Alle regelmäßigen Updates gestoppt ({}). Ich schreibe nur noch auf direkte Anfrage.".format(len(jobs))
        bot.send_message(chat_id=update.message.chat_id, text=message)

        for cur_job in jobs:
            cur_job.schedule_removal()

    def stop_daily(self, bot, update, job_queue):
        self.stop(bot, update, job_queue)

    def start_daily(self, bot, update, job_queue):
        message = "Ich sende ab jetzt jeden Tag um 10 Uhr das Menü in diesen Chat."
        message += '\n' + "Sende mir /stop_daily um das regelmäßige Update zu stopppen."
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text=message)
        job_queue.run_daily(self.daily_menu, datetime.time(10, 36), days=(0, 1, 2, 3, 4),
                            context=chat_id, name=chat_id)

    def menu(self, bot, update, args):
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

    def daily_menu(self, bot, job):
        if job.context:
            message = get_menu_as_string(Mensa.DEFAULT)
            bot.send_message(chat_id=job.context, text=message, parse_mode='Markdown')
        else:
            print("Error!")

    def status(self, bot, update, job_queue):
        message = "Im moment laufen insgesamt {} daily jobs.".format(len(job_queue.jobs()))
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode='Markdown')
