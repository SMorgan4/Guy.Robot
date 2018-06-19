from discord.ext.commands import bot
import settings


class gr_bot(bot.Bot):
    def __init__(self, command_prefix="!"):
        self.settings = settings.settings()
        self.spoiler_mask = '[Spoiler removed react with 🔍 to show]'
        bot.Bot.__init__(self, command_prefix=command_prefix, owner_id=self.settings.owner, case_insensitive=True)
