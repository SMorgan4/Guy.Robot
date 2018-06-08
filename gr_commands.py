import UI
import discord


class SimpleEmbed:
    def __init__(self, ctx, title, text):
        self.bot_message = None
        self.ui = UI.UI(self, element_list=["close"])
        self.text = text
        self.title = title
        self.embed = discord.Embed(title=self.title, description=self.text)
        self.ctx = ctx
        self.user_message = ctx.message

    async def send(self):
        self.bot_message = await self.ctx.send(embed=self.embed)
        await self.ui.build()
        await self.ui.poll(self.ctx.bot)


async def about(ctx, settings):
    title = 'About Guy.Robot'
    text = 'A bot for embedding gaming forum posts into discord.\n' \
           f'To add to your server have an admin accept [this link]({settings.auth_link})\n' \
           "If you're interested in the bot's code check out its [GitHub Page](https://github.com/SMorgan4/Guy.Robot)"
    message = SimpleEmbed(ctx, title, text)
    await message.send()

