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
        self.set_elements(element_list)

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
        await parent().bot_message.delete()
        return False

    async def minimize(self, parent):
        """Sets the message size to minimum. The parent object must implement an update_size function."""
        parent().update_size('std')
        await parent().bot_message.edit(embed=self.parent().embed)
        return True

    async def maximize(self, parent):
        """Sets the message size to maximum. The parent object must implement an update_size function."""
        parent().update_size('max')
        await parent().bot_message.edit(embed=self.parent().embed)
        return True

    async def help(self, parent):
        await parent().help()

# Standard response classes


class UIResponse:
    """Generic class for embedded message with UI"""
    def __init__(self, ctx, message):
        self.bot_message = None
        self.ui = UI(self)
        self.embed = message
        self.ctx = ctx
        self.user_message = ctx.message

    async def send(self):
        """Sends message and starts UI"""
        self.bot_message = await self.ctx.send(embed=self.embed)
        await self.ui.start(self.ctx.bot)


class CloseableResponse(UIResponse):
    """Class for user closable embedded bot messages"""
    def __init__(self, ctx, message):
        UIResponse.__init__(self, ctx, message)
        self.ui = UI(self, element_list=["close"])


class ResizeableResponse(UIResponse):
    """Preview object creates and manages an embed object if supplied with a valid forum link"""
    def __init__(self, ctx, message, settings, size="std"):
        UIResponse.__init__(self, ctx, message)
        self.settings = settings
        self.size = size
        self.lines = []
        self.embed_text = ''

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
            self.embed.description =  self.embed_text
