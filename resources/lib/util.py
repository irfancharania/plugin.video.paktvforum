import requests, re
from xbmcswift2 import xbmcaddon


# allows us to get mobile version
user_agent_mobile = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5'

user_agent_desktop = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0'


def get_image_path(image):
    ''' get image path '''
    addon_id = 'plugin.video.paktvforum'
    image = 'special://home/addons/{id}/resources/images/{image}'.format(id=addon_id, image=image)
    return image


def get_remote_data(url, ismobile=True):
    ''' fetch website data as mobile or desktop browser'''
    user_agent = user_agent_mobile if ismobile else user_agent_desktop

    headers = { 'User-Agent': user_agent }
    r = requests.get(url, headers=headers)
    return r.content


def is_site_available(url):
    ''' ping site to see if it is up '''
    try:
        r = requests.head(url)
        return r.status_code < 400

    except:
        return false


def clean_post_links(linklist):
    ''' There are a lot of mal-formed links
    e.g. <a href='link1'>part of </a><a href='link1'>title</a>
    This method will merge them into a unique dictionary
    '''
    tag_dic = {}

    for li in linklist:
        key = li['href']
        value = li.text

        if value:
            if not (key in tag_dic):
                tag_dic[key] = value
            else:
                tag_dic[key] = tag_dic[key], value

    return tag_dic
