import base64
import string
import random

import mysql.connector.errors
from mysql.connector import (connection)


# https://core.telegram.org/bots/api#message
from UserInfo import UserInfo
from BotSettings import BotSettings

class MysqlDb:
    _config = object
    _db = {}
    _cursor = {}

    def __init__(self, config: BotSettings):
        self._config = config
        self._db = connection.MySQLConnection(user=self._config.mysql_user(),
                                              password=self._config.mysql_password(),
                                              host=self._config.mysql_host())

        self._cursor = self._db.cursor(buffered=False, dictionary=True)

        self._cursor.execute(
            "CREATE DATABASE IF NOT EXISTS " + self._config.mysql_database() + " CHARACTER SET='UTF8';")
        self._db.cmd_init_db(self._config.mysql_database())
        self._cursor.execute("CREATE TABLE IF NOT EXISTS " + self._config.mysql_table_prefix() + "Persons ("
                                                                                                     "id BIGINT NOT NULL,"
                                                                                                     'first_name VARCHAR(255),'
                                                                                                     'last_name VARCHAR(255),'
                                                                                                     'user_name VARCHAR(255),'
                                                                                                     'language_code VARCHAR(3) ,'
                                                                                                     'reg_data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
                                                                                                     'PRIMARY KEY(id)'
                                                                                                     ");")

        self._cursor.execute("CREATE TABLE IF NOT EXISTS `" + self._config.mysql_table_prefix() + "Books` ("
                                                                                                  "`id` int NOT NULL AUTO_INCREMENT,"
                                                                                                  "`name` varchar(140) NOT NULL,"
                                                                                                  "`user_id` bigint,"
                                                                                                  "`write_enable` tinyint NOT NULL DEFAULT '0',"
                                                                                                  "`owner_id` bigint NOT NULL,"
                                                                                                  "PRIMARY KEY (`id`,`owner_id`)"
                                                                 ");")

        self._cursor.execute("CREATE TABLE IF NOT EXISTS `" + self._config.mysql_table_prefix() + "Transactions` ("
                                                                                                      "`book_id` int NOT NULL,"
                                                                                                      "`balance` int NOT NULL,"
                                                                                                      "`datetime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                                                                                                      "`comment` varchar(140) NOT NULL,"
                                                                                                      "`user_id` bigint NOT NULL,"
                                                                                                      "`id` bigint NOT NULL AUTO_INCREMENT,"
                                                                                                      "	PRIMARY KEY (`id`),"
                                                                 "FOREIGN KEY (`user_id`) REFERENCES `"+self._config.mysql_table_prefix()+"Persons`(`id`)"
                                                                     ");")

        self._cursor.execute("CREATE TABLE IF NOT EXISTS `"+self._config.mysql_table_prefix()+"Invites` ("
                                                                                              "`book_id` int NOT NULL,"
                                                                                              "`invite_key` varchar(160) NOT NULL,"
                                                                                              "`expire` DATETIME NOT NULL,"
                                                                                              "PRIMARY KEY (`invite_key`),"
                                                                                              "FOREIGN KEY (`book_id`) REFERENCES `"+self._config.mysql_table_prefix()+"Books`(`id`)"
                                                                                              ");")

    def has_user(self, user_id: int) -> bool:
        result = self._cursor.execute(
            "SELECT COUNT(*) FROM `" + self._config.mysql_table_prefix() + "Persons` WHERE id=" + str(user_id) + ";")
        rows = self._cursor.fetchall()[0].get('COUNT(*)', 0)
        return rows > 0

    def register_user(self, user: UserInfo) -> bool:
        if not user.is_bot():
            try:
                self._cursor.execute("INSERT INTO `" + self._config.mysql_table_prefix()+ "Persons` (id, first_name, last_name, user_name, language_code) VALUES (%s, %s, %s, %s, %s);",
                                     (user.id(), user.first_name(), user.last_name(),
                                      user.username(), user.language_code()))
                self._db.commit()
            except mysql.connector.errors.InternalError as e:
                print("Error: ", e)
                return False
            return True

    def books_list(self, user: UserInfo):
        if user.is_bot():
            return {}
        self._cursor.execute(
            "SELECT * FROM `" + self._config.mysql_table_prefix() + "Books` WHERE user_id=" + str(
                user.id()) + " OR owner_id="+str(user.id())+";")
        rows = self._cursor.fetchall()
        if len(rows) > 0:
            return (len(rows) , rows)
        else:
            return (0, "Нет доступных книг")

    def create_book(self, user: UserInfo, name: str) -> bool:
        try:
            self._cursor.execute("INSERT INTO `"+self._config.mysql_table_prefix()+"Books` (`name`,`user_id`,`write_enable`,`owner_id`) VALUES (%s, %s, %s, %s);",
                                 (name, 0, 1, user.id()))
            self._db.commit()
        except:
            print("Unexpected error")
            return False
        return True

    def get_book_data_last(self, user: UserInfo, list_name: str, idx: int):
        data = {}
        book_params = {}
        try:
            self._cursor.execute("SELECT id, write_enable FROM `"+self._config.mysql_table_prefix()+"Books` WHERE `name`='"+list_name+"' AND `user_id`="+str(user.id())+";")
            book_params = self._cursor.fetchall()
        except:
            print("Unexpected error")
            return (False)

        if (len(book_params) > 0):
            try:
                idx = book_params[0].get('id', None)
                if idx is None:
                    return (False)
                self._cursor.execute("SELECT p.first_name as name, t.`balance`/100 as balance,t.`comment`,t.`datetime` FROM `"+self._config.mysql_table_prefix()+"Transactions` as t, `"+self._config.mysql_table_prefix()+"Persons` as p WHERE `book_id`="+str(idx)+" AND MONTH(`datetime`)=MONTH(now()) and p.id=t.user_id;")
                data = self._cursor.fetchall()
            except:
                print("Unexpected error")
                return (False)

        else:
            return (False)

        return (True, book_params[0].get('id'), book_params[0].get('write_enable', 0), data)

    def get_book_data_current(self, user: UserInfo, list_name: str, idx: int):
        data = {}
        book_params = {}
        try:
            self._cursor.execute("SELECT id, write_enable FROM `"+self._config.mysql_table_prefix()+"Books` WHERE `name`='"+list_name+"' AND (`user_id`="+str(user.id())+" OR `owner_id`='"+str(user.id())+"');")
            book_params = self._cursor.fetchall()
        except:
            print("Unexpected error")
            return (False,)

        if (len(book_params) > 0):
            try:
                idx = book_params[0].get('id', None)
                if idx is None:
                    return (False,)
                self._cursor.execute("SELECT p.first_name as name,t.`balance`/100 as balance,t.`comment`,t.`datetime` FROM `"+self._config.mysql_table_prefix()+"Transactions` as t, `"+self._config.mysql_table_prefix()+"Persons` as p WHERE "
                                                                                                                          "`book_id`="+str(idx)+" "
                                                                                                                                                "AND `datetime`>=DATE_FORMAT(CURDATE(),'%Y-%m-01') and p.id = t.user_id;")

                data = self._cursor.fetchall()
            except:
                print("Unexpected error")
                return (False,)

        else:
            return (False,)

        return (True, book_params[0].get('id'), book_params[0].get('write_enable', 0), data)

    def sum_current_month(self, book_id: int):
        data = {}
        try:
            self._cursor.execute("select p.first_name,sum(t.balance)/100 as total from `"+self._config.mysql_table_prefix()+"Transactions` as t, `"+self._config.mysql_table_prefix()+"Persons` as p where t.book_id = "+str(book_id)+" and t.datetime >= date_format(curdate(), '%Y-%m-01') and p.id=t.user_id group by t.user_id;")
            data = self._cursor.fetchall()
        except:
            print("Unexpected error")
            return (False, data)

        return (True, data)

    def sum_last_month(self, book_id: int):
        data = {}
        try:
            self._cursor.execute(
                "select p.first_name,sum(t.balance)/100 as total from `" + self._config.mysql_table_prefix() + "Transactions` as t, `" + self._config.mysql_table_prefix() + "Persons` as p where t.book_id = " + str(
                    book_id) + " and  t.datetime >= DATE_FORMAT(NOW(), '%Y-%m-01') - INTERVAL 1 MONTH and t.datetime<MONTH(now()) and p.id=t.user_id group by t.user_id;")
            data = self._cursor.fetchall()
        except:
            print("Unexpected error")
            return (False, data)

        return (True, data)

    def add_to_book(self, book_id: int, amount: float, user_id: int, comment: str):
        self._cursor.execute("INSERT INTO `"+self._config.mysql_table_prefix()+"Transactions` (`book_id`, `balance`, `comment`, `user_id`) VALUES (%s, %s, %s, %s)",
                             (book_id, int(amount*100), comment, user_id))
        self._db.commit()

    def clear_old_invites(self):
        self._cursor.execute("DELETE FROM `"+self._config.mysql_table_prefix()+"Invites` WHERE expire < now();")

    def create_book_invite(self, book_id: int):
        self.clear_old_invites()
        key = ""

        self._cursor.execute("SELECT user_id FROM `"+self._config.mysql_table_prefix()+"Books` WHERE `id`="+str(book_id)+" AND `user_id`=0;")
        result = self._cursor.fetchall()

        if len(result) > 0:
            self._cursor.execute("SELECT COUNT(*) FROM `"+self._config.mysql_table_prefix()+"Invites` WHERE `book_id`="+str(book_id)+";")
            result = self._cursor.fetchall()

            if len(result) > 0:
                if result[0].get('COUNT(*)',0) == 0:
                    key = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=96))
                    key = base64.standard_b64encode(key.encode())
                    key = key.decode()
                    try:
                        self._cursor.execute("INSERT INTO `"+self._config.mysql_table_prefix()+"Invites` (`book_id`,`invite_key`,`expire`) VALUES(%s, %s, now() + interval 1 day);",
                                         (book_id, key))
                        self._db.commit()
                    except:
                        key = ""
                        print("Ошибка записи ключа")
                else:
                    self._cursor.execute("SELECT `invite_key` FROM `"+self._config.mysql_table_prefix()+"Invites` WHERE `book_id`="+str(book_id)+";")
                    self._cursor.fetchall()

        return key;

    def check_invite(self, invite: str, user_id: int):
        self.clear_old_invites()

        self._cursor.execute("SELECT book_id FROM `"+self._config.mysql_table_prefix()+"Invites` WHERE `invite_key`='"+invite
                             +"';")
        result = self._cursor.fetchall().get('invite_key', None)

        if len(result) > 0:
            id = result[0].get('book_id', 0)
            self._cursor.execute("UPDATE `"+self._config.mysql_table_prefix()+"Books` SET user_id="+str(user_id)+" WHERE id="+str(id)+";")
            self._cursor.execute("DELETE FROM `"+self._config.mysql_table_prefix()+"Invites` WHERE `invite_key`='"+invite+"';")
            self._db.commit()
            return (True,)
        else:
            return (False, "нет такого ключа")

