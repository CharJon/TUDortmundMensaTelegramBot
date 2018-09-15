import logging
import urllib3
from enum import Enum
import datetime
import re

from telegram.ext import Updater, CommandHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


class Mensa(Enum):
    DEFAULT = 0
    NORD = 1
    SUED = 2
    SONNE = 3


def get_website(mensa):
    http = urllib3.PoolManager()

    if mensa == Mensa.DEFAULT or mensa == Mensa.NORD:
        r = http.request('GET', 'https://www.stwdo.de/mensa-co/tu-dortmund/hauptmensa/')
    elif mensa == Mensa.SUED:
        r = http.request('GET', "https://www.stwdo.de/mensa-co/tu-dortmund/mensa-sued/")
    elif mensa == Mensa.SONNE:
        r = http.request('GET', 'https://www.stwdo.de/mensa-co/fh-dortmund/sonnenstrasse/')
    else:
        r = None

    if r.status == 200:
        return r.data.decode('utf-8')


def get_menu_list_from_html(html):
    s = '<div class="meal-item[^>]*> <[^>]*> <[^>]*alt="([^"]*)[^>]*> <[^>]*> <[^>]*> ([^<]*)'
    pattern = re.compile(s)

    return ((match.group(1), match.group(2)) for match in re.finditer(pattern, html))


def remove_additives(string):
    additives = "\(\d+[a-z]?(,\d+[a-z]?)*\)"
    return remove_whitespaces(re.sub(additives, '', string))


def remove_whitespaces(string):
    multiple_whitespaces = " +"
    return re.sub(multiple_whitespaces, ' ', string)


def menu_list_to_string(menu_list):
    return '\n'.join(
        "*{}*: {}".format(t[0], remove_additives(t[1])) for t in
        menu_list if t[0] not in ("Beilagen", "Grillstation"))


def get_menu_as_string(mensa):
    menu_list = get_menu_list_from_html(get_website(mensa))
    return menu_list_to_string(menu_list)


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


def menu(bot, update):
    if datetime.datetime.today().weekday() < 5:
        message = get_menu_as_string(Mensa.DEFAULT)
    else:
        message = "An Wochenenden sind die Mensen leider geschlossen."

    bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode='Markdown')


def daily_menu(bot, job):
    if job.context:
        message = get_menu_as_string(Mensa.DEFAULT)
        bot.send_message(chat_id=job.context, text=message, parse_mode='Markdown')
    else:
        print("Error!")


def get_token():
    with open('token') as token_file:
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
        menu_handler = CommandHandler('menu', menu)

        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(stop_handler)
        self.dispatcher.add_handler(menu_handler)


if __name__ == '__main__':
    mensa_bot = MensaBot()
