# http://api.telegram.org/bot<API>/getUpdates
# https://github.com/eternnoir/pyTelegramBotAPI
import json
import time

from telebot import types
from telebot import TeleBot
from MysqlDb import MysqlDb
from UserInfo import UserInfo
from BotSettings import BotSettings

config_file = "./config/config.json"

if __name__ == '__main__':
    with open(config_file) as file:
        config = BotSettings(json.load(file))

        db = MysqlDb(config)

        bot = TeleBot(config.telegram_api_token(), parse_mode='HTML')

        def menu(message):
            markup = types.ReplyKeyboardMarkup()
            btn_my_books = types.KeyboardButton('Мои книги')
            btn_help = types.KeyboardButton('Помощь')
            markup.row(btn_my_books, btn_help)
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

        def help_page(message):
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "Помощь:", reply_markup=markup)

        # end of pages

        @bot.message_handler(commands=['start'])
        def send_welcome(message):
            user = UserInfo(message)
            if not db.has_user(user.id()):
                db.register_user(user)

            menu(message)

        @bot.message_handler(content_types=["text"], regexp="^(Мои книги)$")
        def my_books(message):
            markup = types.ReplyKeyboardRemove()
            bot.send_message(message.chat.id, "Ваши книги:", reply_markup=markup)
            db.books_list(UserInfo(message))

        @bot.message_handler(content_types=["text"], regexp="^(Помощь)$")
        def help_btn(message):
            help_page(message)

        @bot.message_handler(commands=['help'])
        def help_cmd(message):
            help_page(message)

        @bot.message_handler(content_types=["text"])
        def echo_all(message):
            menu(message)
        #     userInfo = {}
        #     userInfo['first_name'] = message.from_user.first_name
        #     userInfo['last_name'] = message.from_user.last_name
        #     userInfo['username'] = message.from_user.username
        #     userInfo['language_code'] = message.from_user.language_code
        #     userInfo['id'] = message.from_user.id
        #     userInfo['is_bot'] = message.from_user.is_bot
        #     postInfo = {}
        #     postInfo['date'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.localtime(message.date))
        #     postInfo['content_type'] = message.content_type
        #     postInfo['chat_id'] = message.chat.id
        #     postInfo['text'] = message.text
        #     bot.reply_to(message, message.text)


        bot.polling()
