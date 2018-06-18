import configparser
import json

class settings():
    """Imports settings from Config.cfg"""
    def __init__(self):
        self.max_chars = None
        self.std_lines = None
        self.max_lines = None
        self.line_length = None
        self.auth_link = None
        self.token = None
        self.owner = None
        self.sites = {}
        self.load_bot_settings()
        self.load_forum_settings()

    def load_bot_settings(self):
        config = configparser.ConfigParser()
        config.read('Config.cfg')
        self.max_chars = int(config.get('embed_settings', 'max_chars'))
        self.std_lines = int(config.get('embed_settings', 'std_lines'))
        self.max_lines = int(config.get('embed_settings', 'max_lines'))
        self.line_length = int(config.get('embed_settings', 'line_length'))
        self.auth_link = config.get('discord', 'auth_link')
        self.token = config.get('discord', 'token')
        self.owner = int(config.get('discord', 'owner'))

    def load_forum_settings(self):
        self.sites = {}
        with open('site_settings.json') as forum_data:
            data = forum_data.read()
            forums = json.loads(data)
        for item in forums:
            self.sites[item['name']] = (forum_settings(item['name'], item['base_url'], int(item['color']), item['forum_links']))
        forum_data.close()


class forum_settings():
    """Stores data related to forums for parsing and previews"""
    def __init__(self, name, base_url, color, forum_links: dict):
        self.name = name
        self.base_url = base_url
        self.color = color
        self.forum_links = forum_links

    def __repr__(self):
        return f'Name: {self.name} Base URL: {self.base_url} Color: {self.color}'

    def __str__(self):
        return f'Name: {self.name} Base URL: {self.base_url} Color: {self.color}'
