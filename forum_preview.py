import discord
import forum_parser
import UI


async def forum_preview(message, bot, settings):
    """Creates a preview of a forum post"""
    help_text = 'This is an automatically generated preview of a forum post.\n' \
                'The bot currently supports previews for NeoGAF.com and ResetEra.com\n' \
                "The link's original poster or admins in this channel can resize or delete this preview using" \
                'the emojis below.\nYou may delete this help post by clicking the ✖ emoji below.'
    post = forum_parser.forum_parser(message.content)
    if post.link.url:
        await post.parse()
        if post.post:
            embed = discord.Embed(title=post.title, description=post.content, url=post.link.url)
            if post.avlink:
                embed.set_author(name=post.name, icon_url=post.avlink)
            else:
                embed.set_author(name=post.name)
            if post.images:
                embed.set_image(url=post.images[0])
            if post.link.site == 'era':
                embed.color = 8343994
            embed.set_footer(text=post.site_name, icon_url=post.icon)
            response = UI.ResizeableResponse(message, bot, embed, settings, help_text=help_text)
            await response.send()
