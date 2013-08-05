import abc
from resources.lib.abc_base import BaseForum
from BeautifulSoup import BeautifulSoup
import resources.lib.util as util
import re
import HTMLParser
import resources.lib.category as c

#import logging
#logging.basicConfig(level=logging.DEBUG)

class ThePakTvApi(BaseForum):
    short_name = 'thepaktv'
    long_name = 'The PakTV Forum'
    local_thumb = util.get_image_path('thumb_paktv.png')
    base_url = 'http://www.thepaktv.me/forums/'

    section_url_template = 'forumdisplay.php?f='

###############################################
    category_drama = c.category('Browse Pakistani Dramas',
        [
            {'label': 'Geo',
             'id': '16',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'Ary Digital',
             'id': '18',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'Hum TV',
             'id': '17',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'PTV Home',
             'id': '15',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'Urdu 1',
             'id': '954',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'Geo Kahani',
             'id': '1118',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'A Plus',
             'id': '24',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'TV One',
             'id': '19',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'Express Entertainment',
             'id': '619',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'ARY Musik',
             'id': '25',
             'thumb': util.get_image_path('thumb_paktv.png'),
            },
            {'label': 'ATV',
             'id': '23',
             'thumb': util.get_image_path('thumb_paktv.png'),
            }
        ])

    categories = {
        'drama' : category_drama
    }

    frames = [
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

###############################################

    def get_category_menu(self):
        items = [
            { 'label': value.label,
              'categoryid': key
            } for key, value in self.categories.items()]
        return items


    def get_channel_menu(self, categoryid):
        return self.categories[categoryid].channels


    def get_subforum_id(self, url):
        id = None
        if url:
            f = re.compile('f(\d+)').findall(url)
            if f:
                id = f[0]
        return id


    def get_parents(self, linklist):
        '''identify forum sections/subsections'''
        newlist = []

        for l in linklist:
            if (l.get('id')):
                newlist.append(l)
            else:
                parent = newlist[-1]
                parent['data-has-children'] = True

        return newlist


    def get_show_menu(self, channelid):
        url = '{base}{section}{id}'.format(base=self.base_url,
                        section=self.section_url_template,
                        id=channelid)

        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        sub = soup.find('ul', attrs={'data-role': 'listview', 'data-theme': 'd', 'class': 'forumbits'})
        h = sub.findAll('li')
        linklist = self.get_parents(h)

        shows = []
        episodes = []

        if linklist and len(linklist) > 0:
            for l in linklist:
                tagline = HTMLParser.HTMLParser().unescape(l.a.text)
                link = self.base_url + l.a['href']
                fid = self.get_subforum_id(link)

                data = {
                    'label': tagline,
                    'url': link,
                    'id': fid
                }

                if (l.get('data-has-children')):
                    shows.append(data)
                else:
                    episodes.append(data)

        return shows, episodes


    def get_frame_menu(self):
        return self.frames


    def browse_frame(self, url):
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        items = []

        linklist = soup.findAll('a')

        for l in linklist:
            tagline = HTMLParser.HTMLParser().unescape(l.text)
            link = l['href']

            fid = self.get_subforum_id(link)
            if fid:
                link = self.base_url + self.section_url_template + fid

            items.append({
                'label': tagline,
                'url': link
            })
        sorted_items = sorted(items, key=lambda item: item['label'])
        return sorted_items


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