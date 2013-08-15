from resources.lib.abc_base import BaseForum
from BeautifulSoup import BeautifulSoup
import resources.lib.util as util
import re
import HTMLParser
import resources.lib.structure as s
import resources.lib.hosts as hosts
from resources.lib.post import Post
from xbmcswift2 import xbmcgui


class ThePakTvApi(BaseForum):
    short_name = 'thepaktv'
    long_name = 'The PakTV Forum'
    local_thumb = 'thumb_paktv.png'
    base_url = 'http://www.thepaktv.me/forums/'

    section_url_template = 'forumdisplay.php?f='

###############################################
    category_drama = s.Category('Browse Pakistani Dramas', [
        s.Channel('16', 'Geo', 'geo.png'),
        s.Channel('18', 'Ary Digital', 'ary.png'),
        s.Channel('17', 'Hum TV', 'hum.png'),
        s.Channel('15', 'PTV Home', 'ptv.png'),
        s.Channel('954', 'Urdu 1', 'urdu1.png'),
        s.Channel('1118', 'Geo Kahani', 'geoKahani.png'),
        s.Channel('24', 'A Plus', 'aplus.png'),
        s.Channel('19', 'TV One', 'tv1.png'),
        s.Channel('619', 'Express Entertainment', 'expressEntertainment.png'),
        s.Channel('25', 'ARY Musik', 'aryMusik.png'),
        s.Channel('23', 'ATV', 'atv.png'),
    ])

    category_morning = s.Category('Browse Morning/Cooking Shows', [
        s.Channel('286', 'Morning Shows', 'morning.jpg'),
        s.Channel('141', 'Cooking Shows', 'cooking.jpg'),
    ])

    category_news = s.Category('Browse Current Affairs Talk Shows', [
        s.Channel('26', 'Geo News', 'geoNews.png'),
        s.Channel('27', 'Express News', 'expressNews.png'),
        s.Channel('29', 'Dunya TV', 'dunya.png'),
        s.Channel('28', 'AAJ News', 'aaj.png'),
        s.Channel('53', 'Dawn News', 'dawn.png'),
        s.Channel('30', 'Ary News', 'aryNews.png'),
        s.Channel('735', 'CNBC Pakistan', 'cnbcPakistan.png'),
        s.Channel('31', 'Samaa News', 'samaa.png'),
    ])

    category_ramzan = s.Category('Browse Ramzan Shows', [
        s.Channel('375', 'Ramzan TV Shows'),
        s.Channel('376', 'Ramzan Cooking Shows'),
        s.Channel('400', 'Ramzan Special Dramas & Telefilms'),
    ])

    categories = {
        'drama': category_drama,
        'morning': category_morning,
        'news': category_news,
        'ramzan': category_ramzan,
    }

###############################################
    frames = [
        {'label': 'Today\'s Top Dramas',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/Today/6.html'},
        {'label': 'Today\'s Talk Shows',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/Shows/5.html'},
        {'label': 'Morning Shows',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/MorningShows.html'},
        {'label': 'Hit Dramas',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/HitDramas.html'},
        {'label': 'New Arrivals',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/newdramas.html'},
        {'label': 'Ramdan Kareem Programs',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/Today/ramadan.html'}]

###############################################
    match_string = {
        'tube.php': hosts.youtube,
        'daily.php': hosts.dailymotion,
        'hb.php': hosts.hostingbulk,
        'tune.php': hosts.tunepk,
        'vw.php': hosts.videoweed,
        'fb.php': hosts.facebook,
        'nowvideo.php': hosts.nowvideo,
        'put.php': hosts.putlocker,
    }

###############################################

    def get_category_menu(self):
        items = [{
            'label': value.label,
            'categoryid': key
            } for key, value in self.categories.items()]
        return items

    def get_channel_menu(self, categoryid):
        return self.categories[categoryid].channels

    def get_subforum_id(self, url):
        pk = None
        if url:
            f = re.compile('(?:\?f=|\/f)(\d+)').findall(url)
            if f:
                pk = f[0]
        return pk

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

    # For some reason the fetched request
    # doesn't contain new icons for posts.
    # Also, it doesn't tell me that these are newer
    # from the last time I opened this addon
    # maybe I need to be logged in for that...
    def has_new_episodes(self, listitem):
        if ((listitem.img['src'].find('new') > 0) or
            (listitem.a.img)):
            return True
        return False

    def get_show_menu(self, channelid):
        url = '{base}{section}{id}'.format(
            base=self.base_url,
            section=self.section_url_template,
            id=channelid)

        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        sub = soup.find('ul', attrs={
            'data-role': 'listview', 'data-theme': 'd', 'class': 'forumbits'})
        h = sub.findAll('li')
        linklist = self.get_parents(h)

        channels = []
        shows = []

        if linklist and len(linklist) > 0:
            for l in linklist:
                tagline = HTMLParser.HTMLParser().unescape(l.a.text)
                link = self.base_url + l.a['href']
                fid = self.get_subforum_id(link)

                data = {
                    'label': tagline,
                    'url': link,
                    'pk': fid,
                }

                if (l.get('data-has-children')):
                    channels.append(data)
                else:
                    shows.append(data)

        return channels, shows

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

    def get_episode_menu(self, url, page=1):
        ''' Get episodes for specified show '''

        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        items = []
        next_url = None

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

            if navlink:
                total_pages = int(navlink['data-totalpages'])
                if (total_pages and total_pages > page):
                    pg = url.find('&page=')
                    url = url[:pg] if pg > 0 else url
                    next_url = url + '&page=' + str(page + 1)

        return items, next_url

    def get_episode_data(self, url):
        print 'Get episode data: {url}'.format(url=url)

        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        linklist = soup.find('ol', id='posts').find(
            'blockquote', "postcontent restore").findAll('a')

        # correct links for erroneous formatting
        cleanlinks = util.clean_post_links(linklist)

        # parse post links
        p = Post()

        progress = xbmcgui.DialogProgress()
        progress.create('[B]Processing found links[/B]')
        total = len(cleanlinks)
        current = 0

        for url, text in cleanlinks.items():
            current += 1
            percent = (current * 100) // total
            msg = 'Processing {current} of {total}'.format(
                current=current, total=total)
            progress.update(percent, '', msg, '')

            if progress.iscanceled():
                break

            # process here
            p.add_link(url, text, self.match_string)

        progress.close()

        items = [{
            'label': HTMLParser.HTMLParser().unescape(part.text),
            'partnum': num,
            'media': part.media
        } for num, part in p.parts.items()]

        return items
