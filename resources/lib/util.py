import requests, re
from xbmcswift2 import xbmcaddon


# allows us to get mobile version
user_agent_mobile = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8G4 Safari/6533.18.5'

user_agent_desktop = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0'


def get_image_path(image):
    addon_id = 'plugin.video.paktvforum'
    image = 'special://home/addons/{id}/resources/images/{image}'.format(id=addon_id, image=image)
    return image


def get_remote_data(url, ismobile=True):
    user_agent = user_agent_mobile if ismobile else user_agent_desktop

    headers = { 'User-Agent': user_agent }
    r = requests.get(url, headers=headers)
    return r.content


def is_site_available(url):
    try:
        r = requests.head(url)
        return r.status_code < 400

    except:
        return false

