class UserInfo:
    user_info = {}

    def __init__(self, message):
        self.user_info['first_name'] = message.from_user.first_name
        self.user_info['last_name'] = message.from_user.last_name
        self.user_info['username'] = message.from_user.username
        self.user_info['language_code'] = message.from_user.language_code
        self.user_info['id'] = message.from_user.id
        self.user_info['is_bot'] = message.from_user.is_bot

    def first_name(self):
        return self.user_info.get('first_name', '')

    def last_name(self):
        return self.user_info.get('last_name', '')

    def username(self):
        return self.user_info.get('username', '')

    def language_code(self):
        return self.user_info.get('language_code', 'ru')

    def id(self):
        return self.user_info.get('id', '0')

    def is_bot(self):
        return self.user_info.get('is_bot', False)
