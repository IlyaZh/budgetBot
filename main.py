# http://api.telegram.org/bot<API>/getUpdates
# https://github.com/eternnoir/pyTelegramBotAPI

from Bot import Bot
from Task import Task

config_file = "./config/config.json"

if __name__ == '__main__':
    bot = Bot(config_file)
    bot.start()
