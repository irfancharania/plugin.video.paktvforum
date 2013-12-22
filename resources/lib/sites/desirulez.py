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
    sub_id_regex = '(?:\?f=|\/f|\?t=|\/)(\d+)'

    section_url_template = 'forumdisplay.php?f='
    mobile_style = '&styleid=129'

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

    category_misc = s.Category('Miscellaneous', [
        s.Channel('339', 'MTV', 'mtv.jpg'),
    ])

    categories = {
        'drama': category_drama,
        'news': category_news,
        'misc': category_misc,
    }

###############################################

    match_string = {
        'yt.php': (hosts.youtube, 'v='),
        'youtube.php': (hosts.youtube, 'id='),
        'yw.php': (hosts.youtube, 'id='),
        'dm.php': (hosts.dailymotion, 'v='),
        'tune.php': (hosts.tunepk, 'v='),
        'hb.php': (hosts.hostingbulk, 'v='),
        'nowvideo.php': (hosts.nowvideo, 'v='),
        'now.php': (hosts.nowvideo, 'id='),
        'put.php': (hosts.putlocker, 'id='),
        'weed.php': (hosts.videoweed, 'id='),
        'novamov.php': (hosts.novamov, 'id='),
        'movshare.php': (hosts.movshare, 'id='),
        'dailymotion.com': (hosts.dailymotion, 'video/'),
        'tune.pk': (hosts.tunepk, 'vid='),
        'hostingbulk.com': (hosts.hostingbulk, 'embed-'),
        'youtube.com': (hosts.youtube, 'embed/'),
        'abc.php': (hosts.videotanker, 'id='),
    }

###############################################

    def get_show_menu(self, channelid):
        ''' Get shows for specified channel'''

        url = '{base}{section}{pk}{style}'.format(
            base=self.base_url,
            section=self.section_url_template,
            pk=channelid,
            style=self.mobile_style)

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

    def get_episode_data(self, url):
        url = '{url}{style}'.format(
            url=url, style=self.mobile_style)
        print 'Get episode data: {url}'.format(url=url)

        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        linklist = soup.find('ol', id='posts').find(
            'blockquote', 'postcontent restore').findAll('a')

        # correct links for erroneous formatting
        # and fetch correct link for misleading ids
        cleanlinks = util.find_host_link(util.clean_post_links(linklist))

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
