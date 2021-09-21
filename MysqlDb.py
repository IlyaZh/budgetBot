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
                                                                                                     'firstName VARCHAR(255) NOT NULL,'
                                                                                                     'lastName VARCHAR(255) NOT NULL,'
                                                                                                     'userName VARCHAR(255) NOT NULL,'
                                                                                                     'languageCode VARCHAR(3) ,'
                                                                                                     'regData TIMESTAMP DEFAULT CURRENT_TIMESTAMP,'
                                                                                                     'PRIMARY KEY(id)'
                                                                                                     ");")
        self._cursor.execute("CREATE TABLE IF NOT EXISTS `" + self._config.mysql_table_prefix() + "Transactions` ("
                                                                                                      "`book_id` int NOT NULL,"
                                                                                                      "`balance` int NOT NULL,"
                                                                                                      "`datetime` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"
                                                                                                      "`comment` varchar(140) NOT NULL,"
                                                                                                      "	PRIMARY KEY (`book_id`),"
                                                                                                      "FOREIGN KEY (`book_id`) REFERENCES `" +
                             self._config.mysql_table_prefix() + "Books`(`id`)"
                                                                     ");")

        self._cursor.execute("CREATE TABLE IF NOT EXISTS `" + self._config.mysql_table_prefix() + "Books` ("
                                                                                                      "`id` int NOT NULL,"
                                                                                                      "`user_id` bigint NOT NULL,"
                                                                                                      "`writeEnable` tinyint NOT NULL DEFAULT '0',"
                                                                                                      "`ownerId` bigint NOT NULL,"
                                                                                                      "`invite` varchar(128) NOT NULL,"
                                                                                                      "PRIMARY KEY (`id`,`ownerId`),"
                                                                                                      "FOREIGN KEY (`ownerId`) REFERENCES `" +
                             self._config.mysql_table_prefix() + "Persons`(`id`),"
                                                                     "FOREIGN KEY (`user_id`) REFERENCES `" +
                             self._config.mysql_table_prefix() + "Persons`(`id`)"
                                                                     ");")

    def has_user(self, user_id: int) -> bool:
        result = self._cursor.execute(
            "SELECT COUNT(*) FROM `" + self._config.mysql_table_prefix() + "Persons` WHERE id=" + str(user_id) + ";")
        rows = self._cursor.fetchall()[0].get('COUNT(*)', 0)
        return rows > 0

    def register_user(self, user: UserInfo) -> bool:
        if not user.is_bot():
            try:
                self._cursor.execute("INSERT INTO `" + self._config.mysql_table_prefix()+ "Persons` (id, firstName, lastName, userName, languageCode) VALUES (%s, %s, %s, %s, %s);",
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
                user.id()) + ";")
        rows = self._cursor.fetchall()
        if len(rows) == 0:
            pass
        else:
            pass
