import UI
import discord


async def about(ctx, settings):
    """Provides basic info about the bot"""
    title = 'About Guy.Robot'
    text = 'A bot for embedding gaming forum posts into discord.\n' \
           f'To add to your server have an admin accept [this link]({settings.auth_link})\n' \
           "If you're interested in the bot's code check out its [GitHub Page](https://github.com/SMorgan4/Guy.Robot)"
    response = UI.CloseableResponse(ctx, discord.Embed(title=title, description=text))
    await response.send()
