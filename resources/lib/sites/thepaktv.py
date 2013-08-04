import abc
from resources.lib.abc_base import BaseForum
from BeautifulSoup import BeautifulSoup
import resources.lib.util as util
import re
import HTMLParser

class ThePakTvApi(BaseForum):
    short_name = 'thepaktv'
    long_name = 'The PakTV Forum'
    thumbnail = ''
    base_url = 'http://www.thepaktv.me/forums/'

    section_url_template = 'forumdisplay.php?f='


    def get_frame_menu(self):
        items = [
            {   'label': 'Today\'s Top Dramas',
                'url': 'http://www.paktvnetwork.com/Ads/forum/update3/Today/6.html',
            },
            {   'label': 'Today\'s Talk Shows',
                'url': 'http://www.paktvnetwork.com/Ads/forum/update3/Shows/5.html',
            },
            {   'label': 'Morning Shows',
                'url': 'http://www.paktvnetwork.com/Ads/forum/update3/MorningShows.html',
            },
            {   'label': 'Hit Dramas',
                'url': 'http://www.paktvnetwork.com/Ads/forum/update3/HitDramas.html',
            },
            {   'label': 'New Arrivals',
                'url': 'http://www.paktvnetwork.com/Ads/forum/update3/newdramas.html',
            },
            {   'label': 'Ramdan Kareem Programs',
                'url': 'http://www.paktvnetwork.com/Ads/forum/update3/Today/ramadan.html',
            },
        ]
        return items


    def browse_frame(self, url):
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        items = []

        linklist = soup.findAll('a')

        for l in linklist:
            tagline = HTMLParser.HTMLParser().unescape(l.text)
            link = l['href']
            fid = re.compile('f(\d+)').findall(link)

            if len(fid) > 0:
                link = self.base_url + self.section_url_template + fid[0]

            items.append({
                'label': tagline,
                'url': link
            })
        return items


    def browse_channels(self):
        pass


    def browse_shows(self):
        pass


    def browse_episodes(self, url, page=1):
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        items = []

        container = soup.find('ul', id='threads')
        if container and len(container) > 0:
            linklist = container.findAll('h3')

            for l in linklist:
                tagline = HTMLParser.HTMLParser().unescape(l.a.text)
                link = l.a['href']

                items.append({
                    'label': tagline,
                    'url': self.base_url + link
                })

            navlink = soup.find('div', attrs={'data-role': 'vbpagenav'})
            next_url = None

            if navlink:
                total_pages = int(navlink['data-totalpages'])
                if (total_pages and total_pages > page):
                    pg = url.find('&page=')
                    url = url[:pg] if pg > 0 else url
                    next_url = url + '&page=' + str(page + 1)

        return items, next_url

###########################################################################

    def get_episode_data(self, url):
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        linklist = soup.find('ol', id='posts').find('blockquote', "postcontent restore").findAll('a')

        items = []

        for item in linklist:
            href = item['href']
            ltxt = item.text

            v = href.find('v=')
            if (v > 0):
                vid = href[v+2:]
                tagline = ltxt

                items.append({
                    'label': HTMLParser.HTMLParser().unescape(tagline),
                    'url': ltxt,
                    'vid': vid
                })
        return items

    def play_video(self):
        pass