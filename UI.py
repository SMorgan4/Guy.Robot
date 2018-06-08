import weakref
import asyncio


class UI:
    """Class for managing emoji UI. Includes the following elements by default: min, max, close. Pass a list of element
     names as a tuple to create a custom layout. Supported elements are: min, max, close. """
    def __init__(self, parent, element_list=('max', 'min', 'close')):
        self.parent = weakref.ref(parent)
        self.standard_elements = {'max': ('➕', self.maximize), 'min': ('➖', self.minimize), 'close': ('✖', self.close)}
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
               (user.permissions_in(self.parent().bot_message.channel).administrator and not user.bot)) \
              and reaction.message.id == self.parent().bot_message.id

    async def build(self):
        """Adds reaction buttons."""
        for key in self.elements:
            await self.parent().bot_message.add_reaction(key)

    async def poll(self, bot):
        """Checks if a user has interacted with a UI element and executes its function if so."""
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
