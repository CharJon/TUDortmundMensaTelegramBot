import mensa_bot as mb

if __name__ == '__main__':
    tu_mensa_bot = mb.MensaBot()
    try:
        tu_mensa_bot.start_bot()
    except KeyboardInterrupt:
        print("Exit Because of KeyboardInterrupt.")
        exit()
