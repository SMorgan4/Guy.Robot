import forum_preview
import settings
import gr_commands
import discord
from discord.ext import commands


settings = settings.settings()
bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!gr"))

@bot.event
async def on_message(message):
    if not message.author.bot:
        preview = forum_preview.forum_preview(message, settings)
        if preview.post.link.url:
            await preview.get_post()
            if preview.embed:
                await preview.send()
                await preview.ui.poll(bot)
    await bot.process_commands(message)


@bot.command()
async def gr(ctx):
    await gr_commands.about(ctx, settings)

bot.run(settings.token)
