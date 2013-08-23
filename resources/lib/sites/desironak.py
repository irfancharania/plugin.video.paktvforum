from resources.lib.abc_base import BaseForum
from BeautifulSoup import BeautifulSoup
import resources.lib.util as util
import HTMLParser
import resources.lib.structure as s
import resources.lib.hosts as hosts
from resources.lib.post import Post
from xbmcswift2 import xbmcgui


class DesiRonakApi(BaseForum):
    short_name = 'desironak'
    long_name = 'Desi Ronak Forum'
    local_thumb = 'thumb_desironak.png'
    base_url = 'http://www.desironak.com/forums/'
    sub_id_regex = '\?(\d+)\-'

    section_url_template = 'forumdisplay.php?'
    thread_url_template = 'showthread.php?'
    mobile_styleid = '24'

###############################################
    category_drama = s.Category('Browse Pakistani Dramas', [
        s.Channel('30', 'Geo', 'geo.png'),
        s.Channel('29', 'Ary Digital', 'ary.png'),
        s.Channel('31', 'Hum TV', 'hum.png'),
        s.Channel('460', 'PTV Home', 'ptv.png'),
        s.Channel('1182', 'Urdu 1', 'urdu1.png'),
        s.Channel('1328', 'Geo Kahani', 'geoKahani.png'),
        s.Channel('277', 'A Plus', 'aplus.png'),
        s.Channel('578', 'TV One', 'tv1.png'),
        s.Channel('779', 'Express Entertainment',
                  'expressEntertainment.png'),
        s.Channel('229', 'ARY Musik', 'aryMusik.png'),
        s.Channel('563', 'ATV', 'atv.png'),
        s.Channel('246', 'Aag TV', 'aag.png'),
    ])

    category_morning = s.Category('Browse Morning/Cooking Shows', [
        s.Channel('454', 'Morning Shows', 'morning.png'),
        s.Channel('33', 'Cooking Shows', 'cooking.png'),
    ])

    category_telefilms = s.Category('Browse Stage Dramas/Telefilms/Special Events', [
        s.Channel('235', 'Family Stage Dramas'),
        s.Channel('62', 'Telefilms'),
        s.Channel('88', 'Events'),
    ])

    category_news = s.Category('Browse Current Affairs Talk Shows', [
        s.Channel('355', 'Geo News', 'geoNews.png'),
        s.Channel('400', 'Express News', 'expressNews.png'),
        s.Channel('250', 'Dunya News', 'dunya.png'),
        s.Channel('394', 'AAJ News', 'aaj.png'),
        s.Channel('424', 'Dawn News', 'dawn.png'),
        s.Channel('389', 'Ary News', 'aryNews.png'),
        s.Channel('1005', 'One News', 'newsone.jpg'),
        s.Channel('405', 'Samaa News', 'samaa.png'),
    ])

    categories = {
        'drama': category_drama,
        'morning': category_morning,
        'news': category_news,
        'telefilms': category_telefilms,
    }

###############################################
    frames = [
        {'label': 'Today\'s Dramas',
         'url': 'http://www.desironak.com/forums/cmps_index.php?pageid=dramas',
         'moduleid': 'module17',
         'containstype': s.ThreadType().Episode},
        {'label': 'Today\'s Talk Shows',
         'url': 'http://www.desironak.com/forums/cmps_index.php?pageid=talkshows',
         'moduleid': 'module16',
         'containstype': s.ThreadType().Episode},
    ]

###############################################
    match_string = {
        'youtube.php': (hosts.youtube, 'id='),
        'dailymotion.php': (hosts.dailymotion, 'id='),
        'tnpk.php': (hosts.tunepk, 'url='),
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

    def get_frame_menu(self):
        return self.frames

    def browse_frame(self, frameid, url):
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        frameid = int(frameid)
        moduleid = self.frames[frameid]['moduleid']
        containstype = self.frames[frameid]['containstype']

        items = []

        linklist = soup.find('div', id=moduleid).findAll('a')

        for l in linklist:
            tagline = HTMLParser.HTMLParser().unescape(l.text)
            link = l['href']
            tid = self.get_sub_id(link)

            if tid:
                link = self.base_url + self.thread_url_template + tid

            items.append({
                'label': tagline,
                'url': link,
                'pk': tid
            })
        sorted_items = sorted(items, key=lambda item: item['label'])
        return sorted_items, containstype

    def get_show_menu(self, channelid):
        ''' Get shows for specified channel'''

        url = '{base}{section}{pk}&styleid={styleid}'.format(
            base=self.base_url,
            section=self.section_url_template,
            pk=channelid,
            styleid=self.mobile_styleid)

        print 'Get show menu: {url}'.format(url=url)

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
                fid = self.get_sub_id(link)

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

    def get_episode_menu(self, url, page=1):
        ''' Get episodes for specified show '''

        url = '{url}&styleid={styleid}'.format(
            url=url, styleid=self.mobile_styleid)
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

                tid = self.get_sub_id(link)

                items.append({
                    'label': tagline,
                    'url': self.base_url + link,
                    'pk': tid,
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
        url = '{url}&styleid={styleid}'.format(
            url=url, styleid=self.mobile_styleid)
        print 'Get episode data: {url}'.format(url=url)

        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        linklist = soup.find('ol', id='posts').find(
            'blockquote', 'postcontent restore').findAll('a')

        # correct links for erroneous formatting
        cleanlinks = util.clean_post_links(linklist)

        # parse post links
        p = Post(self.match_string)

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
            p.add_link(url, text)

        progress.close()

        items = [{
            'label': HTMLParser.HTMLParser().unescape(part.text),
            'partnum': num,
            'media': part.media
        } for num, part in sorted(p.parts.items())]

        return items
