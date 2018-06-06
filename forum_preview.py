import discord
import UI
import forum_parser


class forum_preview:
    """Preview object creates and manages an embed object if supplied with a valid forum link"""
    def __init__(self, user_message, settings, size='std'):
        self.user_message = user_message
        self.post = forum_parser.forum_parser(user_message.content)
        self.settings = settings
        self.size = size
        self.lines = []
        self.embed_text = ''
        self.ui = None
        self.embed = None
        self.bot_message = None
        if self.post.post:
            self.get_lines(self.post.content)
            self.build_embed()

    async def send(self):
        """Sends the message and builds UI on completion. Adds the bot message to self."""
        self.bot_message = await self.user_message.channel.send(embed=self.embed)
        await self.build_ui()

    async def build_ui(self):
        """Adds UI to the preview. Cannot be run until the bot has posted a message to add it to."""
        self.ui = UI.UI(self)
        await self.ui.build()

    def build_embed(self):
        """Creates the embed object based on parameters from the parser"""
        self.select_lines()
        if len(self.embed_text) > self.settings.max_chars:
            # self.content = self.embed_text[self.settings.max_chars:]
            self.embed_text = self.embed_text[:self.settings.max_chars]
        if self.embed_text.count('```') % 2 != 0:
            self.embed_text += '```'
        if len(self.lines) > self.no_lines():
            self.embed_text += '\n*Continued...*'
        self.embed = discord.Embed(title=self.post.title, description=self.embed_text, url=self.post.link.url)
        if self.post.avlink:
            self.embed.set_author(name=self.post.name, icon_url=self.post.avlink)
        else:
            self.embed.set_author(name=self.post.name)
        if self.post.images:
            self.embed.set_image(url=self.post.images[0])
        if self.post.link.site == 'era':
            self.embed.color = 8343994
        self.embed.set_footer(text=self.post.site_name, icon_url=self.post.icon)

    def get_lines(self, content):
        """Breaks the messages content into a series of lines roughly corresponding with one line of text on mobile"""
        while content != '':
            new_line = content.split('\n', 1)[0] + '\n'
            if len(new_line) > self.settings.line_length:
                new_line = content[:self.settings.line_length-1]
                content = content[len(new_line):]
            else:
                content = content[len(new_line):]
            self.lines.append(str(new_line))

    def no_lines(self):
        """Returns the number of lines for a given setting"""
        if self.size == 'max':
            no = self.settings.max_lines
        else:
            no = self.settings.std_lines
        if no > len(self.lines):
            no = len(self.lines)
        return no

    def select_lines(self):
        """Selects the specified number of lines places them in embed_text"""
        self.embed_text = ''
        for line in range(0, self.no_lines()):
            self.embed_text += self.lines[line]

    def update_size(self, size):
        """Updates the size of the embed and rebuilds it"""
        if self.size != size:
            self.size = size
            self.build_embed()
