import urllib3
from enum import Enum
import datetime
import re


class Mensa(Enum):
    UNKNOWN = -1
    DEFAULT = 0
    NORD = 1
    SUED = 2
    SONNE = 3

    @staticmethod
    def from_string(string):
        if string == "nord":
            return Mensa.NORD
        elif string == "sued":
            return Mensa.SUED
        elif string == "sonne":
            return Mensa.SONNE
        else:
            return Mensa.UNKNOWN

    @staticmethod
    def get_name(mensa):
        if mensa == Mensa.NORD or mensa == Mensa.DEFAULT:
            return "*Mensa Nord*"
        elif mensa == Mensa.SUED:
            return "*Mensa Sued*"
        elif mensa == Mensa.SONNE:
            return "*Mensa Sonnenstrasse*"
        elif mensa == Mensa.UNKNOWN:
            return "*Mensa unbekannt!*"


def get_website(mensa):
    http = urllib3.PoolManager()

    if mensa == Mensa.DEFAULT or mensa == Mensa.NORD:
        r = http.request('GET', 'https://www.stwdo.de/mensa-co/tu-dortmund/hauptmensa/')
    elif mensa == Mensa.SUED:
        r = http.request('GET', "https://www.stwdo.de/mensa-co/tu-dortmund/mensa-sued/")
    elif mensa == Mensa.SONNE:
        r = http.request('GET', 'https://www.stwdo.de/mensa-co/fh-dortmund/sonnenstrasse/')
    else:
        return None

    if r.status == 200:
        return r.data.decode('utf-8')
    else:
        return None


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
    return Mensa.get_name(mensa) + '\n' + "-------" + '\n' + menu_list_to_string(menu_list)


def get_menu(mensa):
    if datetime.datetime.today().weekday() < 5:
        return get_menu_as_string(mensa)
    else:
        return "An Wochenenden sind die Mensen leider geschlossen."
