import UI
from discord import Embed
from discord.ext import commands
import os
import psutil

class meta_cog:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='gr', aliases=['guyrobot', 'guy.robot'])
    async def about(self, ctx):
        """Provides basic info about the bot"""
        title = 'About Guy.Robot'
        text = 'A bot for embedding gaming forum posts into discord.\n' \
               f'To add to your server have an admin accept [this link]({self.bot.settings.auth_link})\n'
        message = Embed(title=title, description=text)
        owner = ctx.bot.get_user(ctx.bot.owner_id)
        message.add_field(name='Owner', value=f'{owner.name}#{owner.discriminator}')
        message.add_field(name='GitHub', value='[Guy.Robot](https://github.com/SMorgan4/Guy.Robot)')
        message.add_field(name='Servers', value=str(len(ctx.bot.guilds)))
        response = UI.CloseableResponse(ctx.message, ctx.bot, message)
        await response.send()

    @commands.command(name='servers', hidden=True)
    @commands.is_owner()
    async def servers(self, ctx):
        title = 'Current bot servers:'
        text = ''
        for guild in ctx.bot.guilds:
            text += f"{guild.name}\n"
        response = UI.CloseableResponse(ctx.message, ctx.bot, Embed(title=title, description=text))
        await response.send()

    @commands.command(name='process', hidden=True)
    @commands.is_owner()
    async def process(self, ctx):
        pid = os.getpid()
        process = psutil.Process(pid)
        ram = f'{int(process.memory_info().rss/1000000)}MB'
        message = Embed(title="Bot Process info")
        message.add_field(name='PID', value=str(pid))
        message.add_field(name='RAM Usage', value=ram)
        response = UI.CloseableResponse(ctx.message, ctx.bot, message)
        await response.send()

    @commands.command(name='load_bot_settings', hidden='True')
    @commands.is_owner()
    async def load_bot_settings(self, ctx):
        try:
            ctx.bot.settings.load_bot_settings()
            await ctx.send('✔️')
        except:
            pass

    @commands.command(name='load_forum_settings', hidden='True')
    @commands.is_owner()
    async def load_forum_settings(self, ctx):
        try:
            ctx.bot.settings.load_forum_settings()
            await ctx.send('✔️')
        except:
            pass


def setup(bot):
    bot.add_cog(meta_cog(bot))
