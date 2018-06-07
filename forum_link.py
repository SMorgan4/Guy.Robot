import re


class forum_link():
    def __init__(self, message_text):
        """Object for parsing and containing properties of links to a thread or post.
        Era links should take the forms:
        https://www.resetera.com/threads/splatoon-2-physical-is-on-sale-for-50-on-amazon.36571/
        https://www.resetera.com/threads/39971
        https://www.resetera.com/posts/6834173/
        https://www.resetera.com/threads/splatoon-2-physical-is-on-sale-for-50-on-amazon.36571/#post-6834255
        Gaf links should take the forms:
        https://www.neogaf.com/threads/lebron-james-offseason-questions.1462856/#post-253285971
        https://www.neogaf.com/threads/the-official-neogaf-introduce-yourself-thread.1460728/
        """
        self.message_text = message_text
        self.base_links = ['neogaf.com', 'resetera.com']
        self.regs = {'https://www.resetera.com/threads/.+\.\d+': ['era', 'thread'],
                     'https://www.resetera.com/threads/\d+': ['era', 'thread'],
                     'https://www.resetera.com/threads/.+#post-\d+': ['era', 'post'],
                     'https://www.resetera.com/posts/\d+': ['era', 'post'],
                     'https://www.neogaf.com/threads/.+\.\d+': ['gaf', 'thread'],
                     'https://www.neogaf.com/threads/.+#post-\d+': ['gaf', 'post']}
        self.site = None
        self.type = None
        self.url = None
        self.post_id = None

        if self.check_base():
            self.parse_link()

    def check_base(self):
        """Returns true if at least one base url exists in the message"""
        for i in self.base_links:
            if i in self.message_text:
                return True
        return False

    def parse_link(self):
        """Tries to find a valid link to a post or thread, as well as the post id"""
        for key in self.regs:
            p = re.compile(str(key))
            m = p.search(self.message_text)
            if m:
                self.site, self.type = self.regs[key]
                self.url = m.group()
                if self.type == 'post':
                    self.get_post_id()
                    break
        if not self.url:
            print('Unable to parse link in: ' + self.message_text)

    def get_post_id(self):
        """Tries to extract the post ID from the message"""
        if '#post-' in self.message_text:
            self.post_id = self.message_text.split('#post-', 1)[1]
        else:
            ex = re.compile('/\d+/')
            id_match = ex.search(self.message_text)
            self.post_id = id_match.group()
            self.post_id = self.post_id.split('/', 2)[1]
        self.post_id = 'post-' + self.post_id
