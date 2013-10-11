from resources.lib.abc_base import BaseForum
from BeautifulSoup import BeautifulSoup
import resources.lib.util as util
import HTMLParser
import resources.lib.structure as s
import resources.lib.hosts as hosts
import datetime


class ThePakTvApi(BaseForum):
    short_name = 'thepaktv'
    long_name = 'The PakTV Forum'
    local_thumb = 'thumb_paktv.png'
    base_url = 'http://www.thepaktv.me/forums/'
    sub_id_regex = '(?:\?f=|\/f|\?t=)(\d+)'

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
        s.Channel('286', 'Morning Shows', 'morning.png'),
        s.Channel('141', 'Cooking Shows', 'cooking.png'),
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
         'url':
            (
                'http://www.paktvnetwork.com/Ads/forum/update3/Today/{day}.html'
            ).format(day=datetime.datetime.now().weekday() + 1),
         'containstype': s.ThreadType().Show},
        {'label': 'Today\'s Talk Shows',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/Shows/5.html',
         'containstype': s.ThreadType().Show},
        {'label': 'Morning Shows',
         'url':
            'http://www.paktvnetwork.com/Ads/forum/update3/MorningShows.html',
         'containstype': s.ThreadType().Show},
        {'label': 'Hit Dramas',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/HitDramas.html',
         'containstype': s.ThreadType().Show},
        {'label': 'New Arrivals',
         'url': 'http://www.paktvnetwork.com/Ads/forum/update3/newdramas.html',
         'containstype': s.ThreadType().Show},
        {'label': 'Ramdan Kareem Programs',
         'url':
            'http://www.paktvnetwork.com/Ads/forum/update3/Today/ramadan.html',
         'containstype': s.ThreadType().Show}]

###############################################
    match_string = {
        'tube.php': (hosts.youtube, 'v='),
        'daily.php': (hosts.dailymotion, 'v='),
        'hb.php': (hosts.hostingbulk, 'v='),
        'hostingbulk.php': (hosts.hostingbulk, 'v='),
        'tune.php': (hosts.tunepk, 'v='),
        'vw.php': (hosts.videoweed, 'v='),
        'fb.php': (hosts.facebook, 'v='),
        'nowvideo.php': (hosts.nowvideo, 'v='),
        'put.php': (hosts.putlocker, 'v='),
    }

###############################################

    def get_frame_menu(self):
        return self.frames

    def browse_frame(self, frameid, url):
        #print '{name} - fetching {url}'.format(name=self.short_name, url=url)
        data = util.get_remote_data(url)
        soup = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        frameid = int(frameid)
        containstype = self.frames[frameid]['containstype']

        items = []

        linklist = soup.findAll('a')

        for l in linklist:
            tagline = HTMLParser.HTMLParser().unescape(l.text)
            link = l['href']

            fid = self.get_sub_id(link)
            if fid:
                link = self.base_url + self.section_url_template + fid

            items.append({
                'label': tagline,
                'url': link,
                'pk': fid
            })
        sorted_items = sorted(items, key=lambda item: item['label'])
        return sorted_items, containstype
