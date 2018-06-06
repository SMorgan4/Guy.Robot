import discord
import forum_preview
import settings

client = discord.Client()
settings = settings.settings()


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if not message.author.bot:
        preview = forum_preview.forum_preview(message, settings)
        await preview.get_post()
        if preview.embed:
            await preview.send()
            await preview.ui.poll(client)

client.run(settings.token)
