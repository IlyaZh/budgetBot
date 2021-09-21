class BotSettings:
    config_ = {}

    def __init__(self, config):
        self.config_ = config


    def telegram_api_token(self):
        return self.config_.get('TELEGRAM_API_TOKEN', '')


    def mysql_host(self):
        arr = self.config_.get('MYSQL', None)
        if arr is not None:
            return arr.get('HOST', 'localhost')
        return 'localhost'


    def mysql_port(self):
        arr = self.config_.get('MYSQL', None)
        if arr is not None:
            return arr.get('PORT', '3306')
        return '3306'


    def mysql_user(self):
        arr = self.config_.get('MYSQL', None)
        if arr is not None:
            return arr.get('USER', '')
        return ''


    def mysql_password(self):
        arr = self.config_.get('MYSQL', None)
        if arr is not None:
            return arr.get('PASSWORD', '')
        return ''


    def mysql_table_prefix(self):
        arr = self.config_.get('MYSQL', None)
        if arr is not None:
            return arr.get('TABLE_PREFIX', '')
        return ''


    def mysql_database(self):
        arr = self.config_.get('MYSQL', None)
        if arr is not None:
            return arr.get('DATABASE', '')
        return ''
