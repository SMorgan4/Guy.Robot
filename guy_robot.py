import discord
import forum_preview
import settings
from discord.ext import commands

#client = discord.Client()
settings = settings.settings()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    if not message.author.bot:
        preview = forum_preview.forum_preview(message, settings)
        if preview.post.link.url:
            await preview.get_post()
            if preview.embed:
                await preview.send()
                await preview.ui.poll(bot)

#@bot.command()
#async def test(ctx):
#    await ctx.send('success!')

bot.run(settings.token)
