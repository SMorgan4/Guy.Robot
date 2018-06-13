import weakref
import asyncio
import discord

class UI:
    """Class for managing emoji UI. Includes the following elements by default: min, max, close. Pass a list of element
     names as a tuple to create a custom layout. Supported elements are: min, max, close. """
    def __init__(self, parent, element_list=('max', 'min', 'close')):
        self.parent = weakref.ref(parent)
        self.standard_elements = {'max': ('➕', self.maximize), 'min': ('➖', self.minimize), 'close': ('✖', self.close),
                                  'help': ('❓', self.help)}
        self.elements = {}
        self.element_list = list(element_list)
        self.set_elements(self.element_list)

    def add_element(self, element):
        self.element_list.append(element)
        self.set_elements(self.element_list)

    async def remove_element(self, element):
        self.element_list = list(filter(lambda x: x != element, self.element_list))
        #await self.parent().bot_message.clear_reactions()
        self.set_elements(self.element_list)
        #await self.start(self.parent().bot)
        print(self.element_list)

    def set_elements(self, element_list):
        """Creates the list of elements to use in this UI. Supply elements names in a tuple.
        supported elements min, max, close."""
        self.elements = {}
        for element in element_list:
            emoji, func = self.standard_elements[element]
            self.elements[emoji] = func

    def perm_check(self, reaction, user):
        """Checks that the user has sufficient permissions to interact with the UI."""
        return(user == self.parent().user_message.author or
               (user.permissions_in(self.parent().bot_message.channel).administrator and not user.bot))\
                and reaction.message.id == self.parent().bot_message.id

    async def start(self, bot):
        """Adds reaction buttons and polls UI. """
        for key in self.elements:
            await self.parent().bot_message.add_reaction(key)
        try:
            while True:
                user_action = await bot.wait_for('reaction_add', timeout=86400, check=self.perm_check)
                try:
                    print(user_action[1].id)
                    keep_open = await self.elements[str(user_action[0])](self.parent)
                    if not keep_open:
                        break
                except KeyError:
                    pass
        except asyncio.TimeoutError:
            pass

# Standard UI functions
    async def close(self, parent):
        """Deletes the UI element's message."""
        await parent().close()
        return False

    async def minimize(self, parent):
        """Sets the message size to minimum. The parent object must implement an update_size function."""
        if parent().update_size('std'):
            await parent().bot_message.edit(embed=self.parent().embed)
        return True

    async def maximize(self, parent):
        """Sets the message size to maximum. The parent object must implement an update_size function."""
        if parent().update_size('max'):
            await parent().bot_message.edit(embed=self.parent().embed)
        return True

    async def help(self, parent):
        """Responds with the help text for the active command"""
        await parent().add_child(CloseableResponse(parent().user_message, parent().bot,\
                                        discord.Embed(title="Guy.Robot Help", description=parent().help_text), parent=parent))
        await parent().ui.remove_element('help')
        return True

# Standard response classes


class UIResponse:
    """Generic class for embedded message with UI"""
    def __init__(self, user_message, bot, message, help_text, parent=None):
        self.bot_message = None
        self.ui = UI(self)
        self.embed = message
        self.user_message = user_message
        self.bot = bot
        self.help_text = help_text
        self.children = []
        self.parent = parent
        if help_text:
            self.ui.add_element('help')

    async def add_child(self, child):
        self.children.append(child)
        await child.send()

    async def close(self):
        if self.parent:
            self.parent().children.remove(self)
        for child in self.children:
            await child.close()
            self.children.remove(child)
        await self.bot_message.delete()

    async def send(self):
        """Sends message and starts UI"""
        self.bot_message = await self.user_message.channel.send(embed=self.embed)
        await self.ui.start(self.bot)


class CloseableResponse(UIResponse):
    """Class for user closable embedded bot messages"""
    def __init__(self, user_message, bot, message, help_text=None, parent=None):
        UIResponse.__init__(self, user_message, bot, message, help_text, parent)
        self.ui = UI(self, element_list=["close"])


class ResizeableResponse(UIResponse):
    """Creates an embedded message that is resizeable and closeable"""
    def __init__(self, user_message, bot, message, settings, size="std", help_text=None, parent=None):
        UIResponse.__init__(self, user_message, bot, message, help_text, parent)
        self.settings = settings
        self.size = size
        self.lines = []
        self.get_lines(self.embed.description)
        self.select_lines()

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
        """Selects the specified number of lines places them in embed.description"""
        self.embed.description = ''
        for line in range(0, self.no_lines()):
            self.embed.description += self.lines[line]
        if len(self.embed.description) > self.settings.max_chars:
            self.embed.description = self.embed.description[:self.settings.max_chars]
        if self.embed.description.count('```') % 2 != 0:
            self.embed.description += '```'
        if len(self.lines) > self.no_lines():
            self.embed.description += '\n*Continued...*'

    def update_size(self, size):
        """Updates the size of the embed and rebuilds it"""
        if self.size != size:
            self.size = size
            self.select_lines()
            return True
        return False
