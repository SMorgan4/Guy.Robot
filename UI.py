import weakref
import asyncio
import discord
from anytree import NodeMixin, PreOrderIter

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
        self.set_elements(self.element_list)

    def set_elements(self, element_list):
        """Creates the list of elements to use in this UI. Supply elements names in a tuple.
        supported elements min, max, close."""
        self.elements = {}
        for element in element_list:
            emoji, func = self.standard_elements[element]
            self.elements[emoji] = func

    def perm_check(self, reaction, user):
        """Checks that the user has sufficient permissions to interact with the UI."""
        return (self.is_parent_user(user) or self.is_admin) and not user.bot

    def is_parent_user(self, user):
        if user in [node.parent_user for node in PreOrderIter(self.parent().root)]:
            return True

    def is_admin(self, user):
        return user.permissions_in(self.parent().bot_message.channel).administrator

    async def add_reactions(self):
        for key in self.elements:
            await self.parent().bot_message.add_reaction(key)

    async def start(self, bot):
        """Adds reaction buttons and polls UI. """
        await self.add_reactions()
        try:
            keep_open = True
            while keep_open:
                reaction = await bot.wait_for('reaction_add', timeout=86400, check=self.perm_check)
                action = user_action(self.parent, reaction)
                try:
                    for node in PreOrderIter(self.parent().root):
                        if action.message.id == node.bot_message.id:
                            action.parent = weakref.ref(node)
                            keep_open = await node.ui.elements[str(action.emoji)](action)
                except KeyError:
                    pass
        except asyncio.TimeoutError:
            pass


# Standard UI functions
    async def close(self, action):
        """Deletes message."""
        await action.parent().close()
        return False

    async def minimize(self, action):
        """Sets message size to minimum."""
        if action.parent().update_size('std'):
            await action.parent().bot_message.edit(embed=self.parent().embed)
        return True

    async def maximize(self, action):
        """Sets message size to maximum."""
        if action.parent().update_size('max'):
            await action.parent().bot_message.edit(embed=self.parent().embed)
        return True

    async def help(self, action):
        """Shows help message."""
        help_text = action.parent().help_text
        for element in action.parent().ui.elements:
            help_text = f"{help_text}\n{element[0]}: {action.parent().ui.elements[element].__doc__}"
        response = CloseableResponse(action.parent().bot_message, action.parent().bot,\
                                        discord.Embed(title="Guy.Robot Help", description=help_text), parent=action.parent(), parent_user=action.user.id)

        await action.parent().ui.remove_element('help')
        await response.send()
        return True


class user_action:
    """Class containing user ui interactions"""
    def __init__(self, parent, reaction):
        self.emoji = reaction[0]
        self.parent = parent
        self.user = reaction[1]
        self.message = reaction[0].message

# Standard response classes


class UIResponse(NodeMixin):
    """Generic class for embedded message with UI"""
    def __init__(self, user_message, bot, message, help_text, parent=None, parent_user=None, ui_elements=None):
        self.parent = parent
        self.bot_message = None
        if ui_elements:
            self.ui = UI(self, ui_elements)
        else:
            self.ui = UI(self)
        self.embed = message
        self.user_message = user_message
        self.bot = bot
        self.help_text = help_text
        if parent_user:
            self.parent_user = parent_user
        else:
            self.parent_user = user_message.author
        if help_text:
            self.ui.add_element('help')

    async def close(self):
        for node in self.descendants:
            await node.close()
        if self.parent:
            self.parent.children = self.siblings
        await self.bot_message.delete()

    async def send(self):
        """Sends message and starts UI"""
        self.bot_message = await self.user_message.channel.send(embed=self.embed)
        await self.ui.start(self.bot)


class CloseableResponse(UIResponse):
    """Class for user closable embedded bot messages"""
    def __init__(self, user_message, bot, message, help_text=None, parent=None, parent_user=None):
        UIResponse.__init__(self, user_message, bot, message, help_text, parent, parent_user, ui_elements=["close"])


class ResizeableResponse(UIResponse):
    """Creates an embedded message that is resizeable and closeable"""
    def __init__(self, user_message, bot, message, settings, size="std", help_text=None, parent=None, parent_user=None):
        self.settings = settings
        self.size = size
        self.lines = []
        self.get_lines(message.description)
        ui_elements = None
        if len(self.lines) < self.settings.std_lines:
            ui_elements = ["close"]
        UIResponse.__init__(self, user_message, bot, message, help_text, parent, parent_user, ui_elements=ui_elements)
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
