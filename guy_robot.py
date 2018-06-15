import forum_preview
import discord
import sys
import traceback
import gr_bot

bot = gr_bot.gr_bot(command_prefix='!')

initial_extensions = ['cogs.meta', 'cogs.cogs']

# load initial extensions
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="!gr"))


@bot.event
async def on_message(message):
    if not message.author.bot:
        await forum_preview.forum_preview(message, bot)
    await bot.process_commands(message)

bot.run(bot.settings.token)
