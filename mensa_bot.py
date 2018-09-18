import logging

from telegram.ext import Updater, CommandHandler

from mensa_parser import *
import chat_manager as cm

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
        self.add_jobs_from_db_to_queue()
        print("Bot started.")

    def start_bot(self):
        self.updater.start_polling()

    def add_handler(self):
        start_handler = CommandHandler('start', self.start)
        stop_handler = CommandHandler('stop', self.stop, pass_job_queue=True)
        menu_handler = CommandHandler('menu', self.menu, pass_args=True)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(stop_handler)
        self.dispatcher.add_handler(menu_handler)

    def add_jobs_from_db_to_queue(self):
        for entry in cm.chat_manager.get_update_chats():
            self.add_daily_update_job(datetime.time(10, 0), entry[0])

    def start(self, bot, update):
        chat_id = update.message.chat_id

        if cm.chat_manager.update_already_scheduled(chat_id=chat_id, mensa='nord'):
            message = "You already have a daily update scheduled." + '\n' + "You can stop it by telling me to '/stop'."
        else:
            message = "Hey, I will send the menu every weekday at 10:00." + '\n' + "To stop me from doing this send me '/stop'."
            update_time = datetime.time(10, 0)
            update_chat_id = update.message.chat_id

            cm.chat_manager.add_update(update_chat_id, update_time, 'nord')
            self.add_daily_update_job(update_time, update_chat_id)

        bot.send_message(chat_id=chat_id, text=message)

    def add_daily_update_job(self, time, chat_id):
        self.job_queue.run_daily(self.daily_menu, time, days=(0, 1, 2, 3, 4),
                                 context=chat_id, name=chat_id)

    def stop(self, bot, update, job_queue):
        chat_id = update.message.chat_id
        jobs = job_queue.get_jobs_by_name(chat_id)
        bot.send_message(chat_id=chat_id,
                         text="I will stop sending the menu daily to this chat ({}).".format(update.message.chat_id))

        for cur_job in jobs:
            cm.chat_manager.remove_update(chat_id)
            cur_job.schedule_removal()

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
