import json
import time

from telebot import types
from telebot import TeleBot
from MysqlDb import MysqlDb
from UserInfo import UserInfo
from BotSettings import BotSettings

class Bot:
    bot_ = object
    page_ = "main"
    db_ = object
    book_list_ = []
    book_id_ = 0
    def __init__(self, file_config):
        self.page_ = "main"
        with open(file_config) as file:
            config = BotSettings(json.load(file))

            self.db_ = MysqlDb(config)

            self.bot_ = TeleBot(config.telegram_api_token(), parse_mode='HTML', )

            @self.bot_.message_handler(commands=['menu'])
            def menu_page(message):
                self.menu(message)
            # end of pages

            @self.bot_.message_handler(commands=['start'])
            def send_welcome(message):
                user = UserInfo(message)
                if not self.db_.has_user(user.id()):
                    self.db_.register_user(user)

                self.menu(message)

            @self.bot_.message_handler(content_types=["text"], regexp="^(Главное меню)$")
            def main(message):
                self.page_ = "main"
                self.menu(message)

            @self.bot_.message_handler(content_types=["text"], regexp="^(Ввести приглашение)$")
            def invite_page(message):
                chat_id = message.chat.id
                self.page_ = "enter_invite"

                markup = types.ReplyKeyboardMarkup()
                back_btn = types.KeyboardButton('Главное меню')
                markup.row(back_btn)

                self.bot_.send_message(chat_id, "Введите ваше приглашение", reply_markup=markup)

            @self.bot_.message_handler(content_types=["text"], regexp="^(Мои книги)$")
            def my_books(message):
                chat_id = message.chat.id
                self.page_ = "my_book"
                result = self.db_.books_list(UserInfo(message))
                msg = ""
                self.book_id_ = -1

                if result[0] > 0:
                    format = self.format_books_list(result[1])
                    count = format[0]
                    msg = format[1]
                    self.page_ = "select_book"
                    self.book_list_ = format[2]



                markup = types.ReplyKeyboardMarkup()
                btn_add_book = types.KeyboardButton('Создать книгу')
                btn_back = types.KeyboardButton('Главное меню')
                markup.row(btn_add_book, btn_back)
                self.bot_.send_message(chat_id, msg+"Выберите действие:", reply_markup=markup)

            @self.bot_.message_handler(content_types=["text"], regexp="^(Помощь)$")
            def help_btn(message):
                self.help_page(message)

            @self.bot_.message_handler(content_types=["text"], regexp="^(Создать книгу)$")
            def create_book(message):
                chat_id = message.chat.id
                markup = types.ReplyKeyboardMarkup()
                back_btn = types.KeyboardButton('Назад')
                markup.row(back_btn)
                self.bot_.send_message(chat_id, "Введите название книги", reply_markup=markup)
                self.page_ = "add_book"

            @self.bot_.message_handler(content_types=["text"], regexp="^(Назад)$")
            def back_btn(message):
                if self.page_ == "my_book":
                    self.page_ = main
                elif self.page_ == "add_book":
                    self.menu(message)

            @self.bot_.message_handler(commands=['help'])
            def help_cmd(message):
                self.help_page(message)

            @self.bot_.message_handler(content_types=["text"])
            def echo_all(message):
                chat_id = message.chat.id
                user = UserInfo(message)

                if self.page_ == "add_book":
                    self.add_book_page(chat_id, user, message)
                elif self.page_ == "select_book":
                    self.select_book_page(chat_id, user, message)
                elif self.page_ == "book_action":
                    self.book_action(chat_id, user, message)
                elif self.page_ == "add_sum":
                    self.add_sum_action(chat_id, user, message)
                elif self.page_ == "enter_invite":
                    self.check_invite(chat_id, user, message)
                else:
                    self.menu(message)

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
            #     postInfo['chat_id'] = chat_id
            #     postInfo['text'] = message.text
            #     self.bot.reply_to(message, message.text)

    def menu(self, message):
        self.book_id_ = -1
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup()
        btn_my_books = types.KeyboardButton('Мои книги')
        btn_invite = types.KeyboardButton('Ввести приглашение')
        btn_help = types.KeyboardButton('Помощь')
        markup.row(btn_my_books, btn_invite, btn_help)
        self.bot_.send_message(chat_id, "Выберите действие:", reply_markup=markup)

    def add_book_page(self, chat_id: int, user: UserInfo, message):
        if self.db_.create_book(user, message.text):
            result = self.db_.books_list(user)
            if result[0] > 0:
                format = self.format_books_list(result[1])
                count = format[0]
                msg = format[1]
                self.book_list_.clear()
                self.book_list_ = format[2]


                if count > 0:
                    markup = types.ReplyKeyboardMarkup()
                    # btn_add_book = types.KeyboardButton('Создать книгу')
                    btn_back = types.KeyboardButton('Главное меню')
                    markup.row(btn_back)
                    self.bot_.send_message(chat_id, msg, reply_markup=markup)
                    self.page_ = "select_book"
                else:
                    markup = types.ReplyKeyboardMarkup()
                    btn_back = types.KeyboardButton('Главное меню')
                    markup.row(btn_back)
                    self.bot_.send_message(chat_id, "Выберите действие:", reply_markup=markup)

            else:
                msg = result[1]
                if msg == None:
                    msg = "Нет книг"
                self.bot_.send_message(chat_id, msg)
        else:
            self.bot_.send_message(chat_id,
                                   "Произошла ошибка. Попробуйте ещё раз, если повторится, обратитесь к службе поддержки")

    def format_books_list(self, books):
        msg = "Ваши книги:\r\n"
        count = 0;
        book_list = []
        for book in books:
            count += 1
            book_name = book.get('name', "*Странное название*")
            msg += "{:d}) {:s}\r\n".format(count, book_name)
            book_list.append(book_name)
        msg += "\r\n<b>Какую выберите? Введите номер или нажмите кнопку</b>"
        return [count, msg, book_list]

    def select_book_page(self, chat_id: int, user: UserInfo, message):
        try:
            idx = int(message.text)-1
        except ValueError:
            return False
        if idx > len(self.book_list_):
            return (False)

        msg = self.show_book_current(user, idx)

        self.page_ = "book_action"
        markup = types.ReplyKeyboardMarkup()
        add_btn = types.KeyboardButton("Добавить траты");
        last_mounth_btn = types.KeyboardButton("Суммировать прошлый месяц");
        current_mounth_btn = types.KeyboardButton("Суммировать этот месяц");
        back_btn = types.KeyboardButton("Мои книги")
        invite_btn = types.KeyboardButton("Пригласить")
        markup.row(add_btn, last_mounth_btn, current_mounth_btn)
        markup.row(back_btn, invite_btn)

        self.bot_.send_message(chat_id, msg, reply_markup=markup)

    def book_action(self, chat_id: int, user: UserInfo, message):
        if message.text == "Добавить траты":
            self.bot_.send_message(chat_id, "Введите сумму и после пробела комментарий, если нужен")
            self.page_ = "add_sum"
        elif message.text == "Суммировать прошлый месяц":
            sum = self.db_.sum_last_month(self.book_id_)
            is_equals = True

            msg = "<b>Траты за прошлый месяц:</b>\r\n"
            total = 0
            print(sum)
            if sum[0] and len(sum[1]) > 1:
                for who in sum[1]:
                    name = who.get('first_name', "Кто это??")
                    amount = float(who.get('total', 0))
                    total += amount
                    msg += "{:s} потратил(а): {:0.2f} руб.\r\n".format(name, amount)
                msg += "\r\n<b>Кто платит?</b>\r\n"
                count = len(sum[1])
                if count != 0:
                    avg = total / count
                    for who in sum[1]:
                        name = who.get('first_name', "Кто это??")
                        amount = float(who.get('total', 0))
                        debt = amount - avg
                        if debt < 0:
                            is_equals = False
                            msg += "{:s} платит <b>{:0.2f}</b>".format(name, abs(debt))
                        elif debt > 0 and len(sum[1]) > 2:
                            msg += "{:s} должен получить <b>{:0.2f}</b>".format(name, abs(debt))

                    if is_equals:
                        msg += "<b>АРЧИК!</b>"
                        photo = open('./archi.jpg', 'rb')
                        self.bot_.send_photo(chat_id, photo)
            else:
                msg += "нет\r\n\r\n<b>Кто платит?</b>\r\n<b>АРЧИК!</b>"
                photo = open('./archi.jpg', 'rb')
                self.bot_.send_photo(chat_id, photo)
            self.bot_.send_message(chat_id, msg)
        elif message.text == "Суммировать этот месяц":
            sum = self.db_.sum_current_month(self.book_id_)
            print(sum)
            is_equals = True

            msg = "<b>Траты за этот месяц:</b>\r\n"
            total = 0
            if sum[0] and len(sum[1]) > 1:
                for who in sum[1]:
                    name = who.get('first_name', "Кто это??")
                    amount = float(who.get('total', 0))
                    total += amount
                    msg += "{:s} потратил(а): {:0.2f} руб.\r\n".format(name, amount)
                msg += "\r\n<b>Кто платит?</b>\r\n"
                count = len(sum[1])
                if count != 0:
                    avg = total / count
                    for who in sum[1]:
                        name = who.get('first_name', "Кто это??")
                        amount = float(who.get('total', 0))
                        debt = amount - avg
                        if debt < 0:
                            is_equals = False
                            msg += "{:s} платит <b>{:0.2f}</b>".format(name, abs(debt))
                        elif debt > 0 and len(sum[1]) > 2:
                            msg += "{:s} должен получить <b>{:0.2f}</b>".format(name, abs(debt))

                    if is_equals:
                        msg += "<b>АРЧИК!</b>"
                        photo = open('./archi.jpg', 'rb')
                        self.bot_.send_photo(chat_id, photo)
            else:
                msg += "нет\r\n\r\n<b>Кто платит?</b>\r\n<b>АРЧИК!</b>"
                photo = open('./archi.jpg', 'rb')
                self.bot_.send_photo(chat_id, photo)
            self.bot_.send_message(chat_id, msg)
        elif message.text == "Пригласить":
            key = self.db_.create_book_invite(self.book_id_)
            if len(key) > 0:
                self.bot_.send_message(chat_id, "Отправьте этот ключ человеку, он <b>получит полный доступ</b> к книге. Ключ является одноразовым и <b>действителен в течени 24 часов</b>, время пошло!.\r\n\r\n{:s}".format(key))
            else:
                self.bot_.send_message(chat_id, "Не удалось сформировать ключ, возможно вы уже создали один и он не истек или уже пригласили кого-то ранее")
            self.page_ = "my_books"
        else:
            self.page_ = "my_books"

    def add_sum_action(self, chat_id: int, user: UserInfo, message):
        str = message.text
        data = str.split(" ")
        amount = 0
        comment = ""
        if len(data) >= 2:
            try:
                amount = float(data[0])
            except ValueError:
                self.bot_.send_message(chat_id, "Странное значение")
                return

            comment = data[1]
        elif len(data) == 1:
            try:
                amount = float(data[0])
            except ValueError:
                self.bot_.send_message(chat_id, "Странное значение")
                return

        if amount != 0:
            self.db_.add_to_book(self.book_id_, amount, user.id(), comment)
            self.bot_.send_message(chat_id, 'Транзакция добавлена "{:0.2f} {:s}"'.format(amount, comment))
            self.page_ = "book_action"


    def show_book_current(self, user: UserInfo, idx: int):
        transactions = self.db_.get_book_data_current(user, self.book_list_[idx], idx)
        msg = ""
        if transactions[0]:
            msg = "Данные за текущий месяц:\n"
            self.book_id_ = transactions[1]

            i = 0
            for item in transactions[3]:
                i += 1
                msg += "{:d} {:0.2f} {:s} {:s}\r\n".format(i, item['balance'], item['comment'], item['name'])
        else:
            msg = "Нет данных за текущий месяц"

        return msg

    def show_book_last(self, user: UserInfo, idx: int):
        transactions = self.db_.get_book_data_last(user, self.book_list_[idx], idx)
        msg = ""
        if transactions[0]:
            msg = "Данные за последний месяц:\n"
            self.book_id_ = transactions[1]

            i = 0
            for item in transactions[3]:
                i += 1
                msg += "{:d} {:0.2f} {:s} {:s}\r\n".format(i, item['balance'], item['comment'], item['name'])
        else:
            msg = "Нет данных за последний месяц"

        return msg

    def check_invite(self, chat_id: int, user: UserInfo, message):
        invite = message.text
        msg = ""

        is_good = self.db_.check_invite(invite, user.id())
        if is_good:
            msg = "Книга успешно добавлена!"
        else:
            msg = "Ошибка"

        self.bot_.send_message(chat_id, msg)
        self.menu(message)

    def help_page(self, message):
        chat_id = message.chat.id
        self.bot_.send_message(chat_id, "Помощи надо?")

    def start(self):
        self.bot_.polling()
