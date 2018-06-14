import configparser


class settings():
    """Imports settings from Config.cfg"""
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('Config.cfg')
        self.max_chars = int(self.config.get('embed_settings', 'max_chars'))
        self.std_lines = int(self.config.get('embed_settings', 'std_lines'))
        self.max_lines = int(self.config.get('embed_settings', 'max_lines'))
        self.line_length = int(self.config.get('embed_settings', 'line_length'))
        self.auth_link = self.config.get('discord', 'auth_link')
        self.token = self.config.get('discord', 'token')
        self.owner = int(self.config.get('discord', 'owner'))
