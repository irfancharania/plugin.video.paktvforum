from resources.lib.abc_base import BaseForum
from BeautifulSoup import BeautifulSoup
import resources.lib.util as util
import HTMLParser
import resources.lib.structure as s
import resources.lib.hosts as hosts
from resources.lib.post import Post
from xbmcswift2 import xbmcgui


class DesiRulezApi(BaseForum):
    short_name = 'desirulez'
    long_name = 'Desi Rulez Forum'
    local_thumb = 'thumb_desirulez.png'
    base_url = 'http://www.desirulez.net/'
    sub_id_regex = '(?:\?f=|\/f|\?t=)(\d+)'

    section_url_template = 'forumdisplay.php?f='
    mobile_styleid = '129'

###############################################
    category_drama = s.Category('Browse Pakistani Dramas', [
        s.Channel('413', 'Geo', 'geo.png'),
        s.Channel('384', 'Ary Digital', 'ary.png'),
        s.Channel('448', 'Hum TV', 'hum.png'),
        s.Channel('1411', 'PTV Home', 'ptv.png'),
        s.Channel('1721', 'Urdu 1', 'urdu1.png'),
        s.Channel('2057', 'Geo Kahani', 'geoKahani.png'),
        s.Channel('1327', 'A Plus', 'aplus.png'),
        s.Channel('1859', 'TV One', 'tv1.png'),
        s.Channel('1412', 'Express Entertainment', 'expressEntertainment.png'),
    ])

    category_news = s.Category('Browse Current Affairs Talk Shows', [
        s.Channel('1039', 'Geo News', 'geoNews.png'),
        s.Channel('1040', 'Express News', 'expressNews.png'),
        s.Channel('1042', 'Dunya TV', 'dunya.png'),
        s.Channel('1038', 'AAJ News', 'aaj.png'),
        s.Channel('1041', 'Ary News', 'aryNews.png'),
        s.Channel('1043', 'Samaa News', 'samaa.png'),
    ])

    categories = {
        'drama': category_drama,
        'news': category_news,
    }

###############################################

    match_string = {
        'yt.php': (hosts.youtube, 'v='),
        'yw.php': (hosts.youtube, 'id='),
        'dm.php': (hosts.dailymotion, 'v='),
        'tune.php': (hosts.tunepk, 'v='),
        'hb.php': (hosts.hostingbulk, 'v='),
        'nowvideo.php': (hosts.nowvideo, 'v='),
        'put.php': (hosts.putlocker, 'id='),
        'weed.php': (hosts.videoweed, 'id='),
        'novamov.php': (hosts.novamov, 'id='),
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

        channels = []
        shows = []

        try:
            sub = soup.find('ul', attrs={
                'data-role': 'listview',
                'data-theme': 'd',
                'class': 'forumbits'})
            h = sub.findAll('li')
            linklist = self.get_parents(h)

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
        except:
            pass

        # This forum has a number of uncategorized threads.
        # Display uncategorized episode threads under Uncategorized
        container = soup.find('ul', id='threads')
        if container and len(container) > 0:
            shows.append({
                'label': '[COLOR white][B]Uncategorized Episodes[/B][/COLOR]',
                'url': url,
                'pk': channelid,
            })

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
        } for num, part in p.parts.items()]

        return items
