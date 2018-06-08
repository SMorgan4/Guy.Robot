import UI
import discord


class SimpleEmbed:
    """Class for user closable embedded bot messages without min/ max functions"""
    def __init__(self, ctx, title, text):
        self.bot_message = None
        self.ui = UI.UI(self, element_list=["close"])
        self.embed = discord.Embed(title=title, description=text)
        self.ctx = ctx
        self.user_message = ctx.message

    async def send(self):
        """Sends message and starts UI"""
        self.bot_message = await self.ctx.send(embed=self.embed)
        await self.ui.start(self.ctx.bot)


async def about(ctx, settings):
    """Provides basic info about the bot"""
    title = 'About Guy.Robot'
    text = 'A bot for embedding gaming forum posts into discord.\n' \
           f'To add to your server have an admin accept [this link]({settings.auth_link})\n' \
           "If you're interested in the bot's code check out its [GitHub Page](https://github.com/SMorgan4/Guy.Robot)"
    message = SimpleEmbed(ctx, title, text)
    await message.send()
