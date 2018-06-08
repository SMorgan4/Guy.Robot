from bs4 import BeautifulSoup
import forum_link
import re
import aiohttp


class forum_parser:
    """Parses a post and stores its data"""
    def __init__(self, message_text):
        self.site_base_url = {'era': 'https://www.resetera.com/', 'gaf': 'https://neogaf.com/'}
        self.post = None
        self.name = None
        self.avlink = None
        self.content = None
        self.title = None
        self.images = []
        self.videos = []
        self.icon = None
        self.site_name = None
        self.link = forum_link.forum_link(message_text)

    async def parse(self):
        """Gets the page and runs all parsing operations"""
        page = await self.get_page()
        if page:
            self.get_meta(page)
            self.get_post(page)
            if self.post:
                self.get_name()
                self.get_avlink()
                self.twitter_embed()
                self.format_images()
                self.youtube_embed()
                self.format_quotes()
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
        self.icon = page.find('meta', property='og:image')['content']
        self.site_name = page.find('meta', property='og:site_name')['content']

    def get_post(self, page):
        """Gets a post from a page"""
        if self.link.site == 'era':
            if self.link.type == 'post':
                self.post = page.find("li", id=self.link.post_id)
            else:
                for post in page.findAll('li', class_="message"):
                    if post.find("acronym", title="Original Poster"):
                        self.post = post
                        break
        elif self.link.site == 'gaf':
            if self.link.type == 'post':
                self.post = page.find('article', {'data-content': self.link.post_id})
            else:
                self.post = page.find('span', class_='thread-op').parent.parent
        if not self.post:
            print(f'Error identifying post in {self.link.site} {self.link.type}: {self.link.url}')

    def get_name(self):
        self.name = self.post.find("a", itemprop="name").get_text()

    def get_avlink(self):
        """Gets the link to the poster's avatar"""
        avlink = self.post.find('a', class_="avatar")
        avlink = avlink.find("img")
        if avlink:
            self.avlink = self.site_base_url[self.link.site] + avlink["src"]
            avlink.decompose()

    def get_contents(self):
        """Gets the post text"""
        if self.link.site == 'era':
            self.content = self.post.find('div', class_="messageContent")
        else:
            self.content = self.post.find('div', class_="bbWrapper")
        for tag in self.content.findAll('script'):
            tag.decompose()
        self.mark_down_links()
        self.content = self.content.get_text()
        self.content = re.sub('\n+', '\n', self.content)
        if self.content.startswith('\n'):
            self.content = self.content[1:]

    def mark_down_links(self):
        """Marks down all links in a post. Runs after format quotes as to not mark down links within quotes because
        marked down links are not supported within the code blocks the bot uses for quotes."""
        for tag in self.content.findAll('a', href=True):
            if tag.get_text() != '':
                mark_down = f"[{tag.get_text()}]({tag['href']})"
                tag.replace_with(mark_down)

    def format_quotes(self):
        """"Wraps quotes in code tag for aesthetics. Adds quote attribution link where possible."""
        if self.link.site == 'era':
            for attribution in self.post.findAll('div', class_="attribution type"):
                self.attribute_quote(attribution)
            for tag in self.post.findAll('div', class_="quote"):
                tag.replace_with(f"```{tag.get_text()}```")
            for tag in self.post.findAll('div', class_="quoteExpand"):
                tag.decompose()
        if self.link.site == 'gaf':
            for tag in self.post.findAll('div', class_=re.compile('bbCodeBlock.+quote')):
                attribution = tag.find('a', class_='bbCodeBlock-sourceJump')
                if attribution:
                    self.attribute_quote(attribution)
                quote = tag.find('div', class_='bbCodeBlock-expandContent')
                quote.replace_with(f"```{quote.get_text()}```")
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
            tag.replace_with(f"[{text} said:]({self.site_base_url[self.link.site] + link})")
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
            count = 0
            for tag in self.post.findAll('img', class_="smilie"):
                tag.replace_with(self.images[count] + '\n')
                tag.decompose()
                count += 1

    def twitter_embed(self):
        """Creates a link to Twitter from a Twitter embed."""
        for tag in self.post.findAll('iframe', attrs={'data-s9e-mediaembed': 'twitter'}):
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
