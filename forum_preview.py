import discord
import forum_parser
import UI


async def forum_preview(message, bot):
    """Creates a preview of a forum post"""
    help_text = 'This is an automatically generated preview of a forum post.\n' \
                'The bot currently supports previews for NeoGAF.com and ResetEra.com\n'
    if message.embeds:
        # if not embed previews are suppressed
        post = forum_parser.forum_parser(message, bot)
        if post.link.url:
            await post.parse()
            if post.post:
                embed = discord.Embed(title=post.title, description=post.content, url=post.link.url)
                if post.avlink:
                    embed.set_author(name=post.name, icon_url=post.avlink, url=post.poster_link)
                else:
                    embed.set_author(name=post.name)
                if post.images:
                    embed.set_image(url=post.images[0])
                embed.color = bot.settings.sites[post.link.site].color
                embed.set_footer(text=post.site_name, icon_url=post.icon)
                response = UI.ResizeableResponse(message, bot, embed, help_text=help_text)
                await response.send()
