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
        self.token = None
        self.get_token()

    def get_token(self):
        """Selects the bot's token at runtime"""
        valid = False
        while not valid:
            mode = input('Mode: Test or release (T/R):').lower()
            if mode == 't':
                mode = 'test'
                valid = True
            elif mode == 'r':
                mode = 'release'
                valid = True
        print(f'Loading {mode} settings')
        self.token = self.config.get('discord_token', mode)
