from bs4 import BeautifulSoup
import forum_link
import re
import aiohttp
from datetime import datetime


class forum_parser:
    """Parses a post and stores its data"""
    def __init__(self, message, bot):
        self.post = None
        self.name = None
        self.avlink = None
        self.content = None
        self.title = None
        self.images = []
        self.videos = []
        self.spoilers = []
        self.icon = None
        self.site_name = None
        self.poster_link = None
        self.bot = bot
        self.timestamp = None
        self.link = forum_link.forum_link(message, bot.settings.sites)
        if self.link:
            self.base_url = bot.settings.sites[self.link.site].base_url

    def __bool__(self):
        if self.post:
            return True
        else:
            return False

    async def parse(self):
        """Gets the page and runs all parsing operations"""
        page = await self.get_page()
        if page:
            self.get_meta(page)
            self.get_post(page)
            if self.post:
                self.get_name()
                self.get_avlink()
                self.get_time()
                self.twitter_embed()
                self.format_images()
                self.youtube_embed()
                self.format_quotes()
                self.format_spoilers()
                self.get_contents()

    async def get_page(self):
        """Gets the forum page"""
        with aiohttp.ClientSession() as a_session:
            async with a_session.get(self.link.url) as response:
                if response.status == 200:
                    page = BeautifulSoup(await response.text(), 'html.parser')
                    return page

    def get_meta(self, page):
        """Gets page, icon and title from metatags, should work for all forums"""
        self.title = page.find('meta', property='og:title')['content']
        if page.find('meta', property='og:image'):
            self.icon = page.find('meta', property='og:image')['content']
        elif page.find('link', rel="icon"):
            self.icon = page.find('link', rel="icon")['href']
        self.site_name = page.find('meta', property='og:site_name')['content']

    def get_post(self, page):
        """Gets a post from a page"""
        if self.link.site == 'era':
            if self.link.type == 'post':
                self.post = page.find("article", id=f"js-{self.link.post_id}")
            else:
                self.post = page.find("article")
        elif self.link.site == 'gaf':
            if self.link.type == 'post':
                self.post = page.find('article', {'data-content': self.link.post_id})
            else:
                self.post = page.find('span', class_='thread-op').parent.parent
        if not self.post:
            print(f'Error identifying post in {self.link.site} {self.link.type}: {self.link.url}')

    def get_name(self):
        poster = self.post.find("a", itemprop="name")
        self.name = poster.get_text()
        self.poster_link = poster['href']
        if self.poster_link.startswith('/'):
            self.poster_link = self.poster_link[1:]
        self.poster_link = self.base_url + self.poster_link

    def get_avlink(self):
        """Gets the link to the poster's avatar"""
        avlink = self.post.find('a', class_="avatar")
        avlink = avlink.find("img")
        if avlink:
            self.avlink = self.base_url + avlink["src"]
            avlink.decompose()

    def get_time(self):
        timestamp = None
        if self.post.find('span', class_="DateTime"):
            timestamp = self.post.find('span', class_="DateTime")["title"]
            timestamp = datetime.strptime(timestamp, '%b %d, %Y at %H:%M %p')
        elif self.post.find('time', class_="u-dt"):
            timestamp = datetime.fromtimestamp(int(self.post.find('time', class_="u-dt")["data-time"]))
        if timestamp:
            self.timestamp = timestamp.astimezone()

    def get_contents(self):
        """Gets the post text"""
        if self.link.site == 'era':
            self.content = self.post.find('div', class_="bbWrapper")
        else:
            self.content = self.post.find('div', class_="bbWrapper")
        for tag in self.content.findAll('script'):
            tag.decompose()
        self.content = self.mark_down_links(self.content)
        self.content = self.content.get_text().strip()
        self.content = re.sub('\n+', '\n', self.content)

    def mark_down_links(self, content):
        """Marks down all links in a post. Runs after format quotes as to not mark down links within quotes because
        marked down links are not supported within the code blocks the bot uses for quotes."""
        for tag in content.findAll('a', href=True):
            if tag.get_text() != '':
                mark_down = f"[{tag.get_text()}]({tag['href']})"
                tag.replace_with(mark_down)
        return content

    def format_quotes(self):
        """"Wraps quotes in code tag for aesthetics. Adds quote attribution link where possible."""
        if self.link.site == 'era':
            for attribution in self.post.findAll('div', class_="attribution type"):
                self.attribute_quote(attribution)
            for tag in self.post.findAll('div', class_="quote"):
                tag.replace_with(f"```{tag.get_text().strip()}```")
            for tag in self.post.findAll('div', class_="quoteExpand"):
                tag.decompose()
        if self.link.site == 'gaf':
            for tag in self.post.findAll('div', class_=re.compile('bbCodeBlock.+quote')):
                attribution = tag.find('a', class_='bbCodeBlock-sourceJump')
                if attribution:
                    self.attribute_quote(attribution)
                quote = tag.find('div', class_='bbCodeBlock-expandContent')
                quote.replace_with(f"```{quote.get_text().strip()}```")
                tag.find('div', class_='bbCodeBlock-expandLink').decompose()

    def attribute_quote(self, tag):
        """Gets the original poster and links to the original post if available"""
        text = tag.get_text()
        text = text.split("said:")[0]
        if self.link.site == 'era':
            link = tag.find('a', href=True)['href']
        elif self.link.site == 'gaf':
            link = tag['href']
        if link:
            tag.replace_with(f"[{text} said:]({self.base_url + link})")
        else:
            tag.replace_with(f"{text} said:")

    def format_images(self):
        """Creates a list of images. Changes image tag to a URL."""
        for tag in self.post.findAll('img', class_=re.compile("bb")):
            self.images.append(tag["src"])
            if self.link.site == 'era':
                tag.replace_with(tag["src"])
            else:
                tag.decompose()
        if self.link.site == 'gaf':
            for count, tag in enumerate(self.post.findAll('img', class_="smilie")):
                tag.replace_with(self.images[count] + '\n')
                tag.decompose()

    def format_spoilers(self):
        for tag in self.post.findAll('div', class_="SpoilerTarget bbCodeSpoilerText"):
            tag = self.mark_down_links(tag)
            self.spoilers.append(tag.get_text().strip())
            tag.replace_with(self.bot.spoiler_mask)
        for tag in self.post.findAll('button', class_='button bbCodeSpoilerButton ToggleTrigger Tooltip JsOnly'):
            tag.decompose()
        for tag in self.post.findAll('div', class_="bbCodeBlock bbCodeBlock--spoiler"):
            tag = self.mark_down_links(tag)
            self.spoilers.append(tag.get_text().strip())
            tag.replace_with(self.bot.spoiler_mask)
        for tag in self.post.findAll('button', class_='bbCodeSpoiler-button button'):
            tag.decompose()

    def twitter_embed(self):
        """Creates a link to Twitter from a Twitter embed."""
        for tag in self.post.findAll('iframe', attrs={'data-s9e-mediaembed': 'twitter'}):
            if self.link.site == 'era':
                tweet_id = tag['data-s9e-lazyload-src'].split('.html#')[1]
            else:
                tweet_id = tag['src'].split('.html#')[1]
            tag.replace_with('https://twitter.com/user/status/' + tweet_id)

    def youtube_embed(self):
        """Creates a link to Youtube from a youtube embed. Adds to a list of video links."""
        tags = None
        if self.link.site == 'era':
            tags = self.post.findAll('span', attrs={'data-s9e-mediaembed': 'youtube'})
        elif self.link.site == 'gaf':
            tags = self.post.findAll('div', class_='bbMediaWrapper')
        for tag in tags:
            url = tag.find('iframe')['src']
            self.videos.append(url)
            tag.replace_with(url)
