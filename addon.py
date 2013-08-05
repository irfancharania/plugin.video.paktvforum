from xbmcswift2 import Plugin, xbmc, xbmcgui, xbmcaddon
import abc
from resources.lib.abc_base import BaseForum
from resources.lib.sites import *
import resources.lib.util as util
import resources.lib.errors as errors
from operator import itemgetter


plugin = Plugin()

@plugin.route('/')
def index():
    items = [{
        'label': sc.long_name,
        'path': plugin.url_for('get_category_menu', siteid=index, cls=sc.__name__),
        'thumbnail': sc.local_thumb,
        'icon': sc.local_thumb,
        } for index, sc in enumerate(BaseForum.__subclasses__())]

    items.append({
        'label': 'Url Resolver Settings',
        'path': plugin.url_for('get_urlresolver_settings'),
        })
    return items


@plugin.route('/urlresolver/')
def get_urlresolver_settings():
    import urlresolver

    urlresolver.display_settings()
    return


@plugin.route('/sites/<cls>/')
def get_category_menu(cls):
    siteid = int(plugin.request.args['siteid'][0])
    api = BaseForum.__subclasses__()[siteid]()

    plugin.log.debug('browse site: {site}'.format(site=cls))

    '''
    # check if site is available
    if api.base_url:
        available = util.is_site_available(api.base_url)

        if available:


    else:
        msg = 'Base url not implemented'
        plugin.log.error(msg)
        raise Exception(msg)
    '''

    frameitems = []
    categoryitems = []

    # get frames
    f = api.get_frame_menu()
    if f:
        frameitems = [{
            'label': item['label'],
            'path': plugin.url_for('browse_frame', siteid=siteid, cls=cls,
                frameid=index, url=item['url'])
        } for index, item in enumerate(f)]

    # get categories
    c = api.get_category_menu()
    if c:
        categoryitems = [{
            'label': item['label'],
            'path': plugin.url_for('browse_category', siteid=siteid, cls=cls,
                categoryid=item['categoryid'])
        } for item in c]

    by_label = itemgetter('label')
    items = frameitems + sorted(categoryitems, key=by_label)
    return items


@plugin.route('/sites/<cls>/category/<categoryid>/')
def browse_category(cls, categoryid):
    siteid = int(plugin.request.args['siteid'][0])
    api = BaseForum.__subclasses__()[int(siteid)]()

    plugin.log.debug('browse category: {category}'.format(category=categoryid))

    items = [{
        'label': item['label'],
        'thumbnail': item.get('thumb', ''),
        'icon': item.get('thumb', ''),
        'path': plugin.url_for('browse_channels', siteid=siteid, cls=cls,
            channelid=item['id'])
    } for item in api.get_channel_menu(categoryid)]

    by_label = itemgetter('label')
    return sorted(items, key=by_label)


@plugin.route('/sites/<cls>/frames/<frameid>/')
def browse_frame(cls, frameid):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    plugin.log.debug('browse frame: {frame}'.format(frame=url))

    items = [{
        'label': item['label'],
        'path': plugin.url_for('browse_shows', siteid=siteid, cls=cls,
            frameid=frameid, showid=index, showpage=1, url=item['url'])
    } for index, item in enumerate(api.browse_frame(url))]

    return items


@plugin.route('/sites/<cls>/channels/<channelid>/')
def browse_channels(cls, channelid):
    siteid = int(plugin.request.args['siteid'][0])
    api = BaseForum.__subclasses__()[int(siteid)]()

    plugin.log.debug('browse channel: {channel}'.format(channel=channelid))

    shows, episodes = api.get_show_menu(channelid)

    episodeitems = [{
        'label': item['label'],
        'path': plugin.url_for('browse_shows', siteid=siteid, cls=cls,
            showid=item['id'], showpage=1, url=item['url'])
    } for item in episodes]

    showitems = [{
        'label': item['label'],
        'path': plugin.url_for('browse_channels', siteid=siteid, cls=cls,
            channelid=item['id'], url=item['url'])
    } for item in shows]

    items = episodeitems + showitems
    return items


@plugin.route('/sites/<cls>/shows/<showid>/<showpage>/')
def browse_shows(cls, showid, showpage=1):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    showpage = int(showpage)

    plugin.log.debug('browse show: {show}'.format(show=url))

    videos, next_url = api.browse_episodes(url, showpage)

    items = [{
        'label': item['label'],
        'path': plugin.url_for('get_episode_data', siteid=siteid, cls=cls,
            showid=showid, showpage=1, episodeid=index, url=item['url'])
    } for index, item in enumerate(videos)]

    if next_url:
        items.append({
            'label': 'Next >>',
            'path': plugin.url_for('browse_shows', siteid=siteid,
                    cls=cls, showid=showid, showpage=str(showpage + 1), url=next_url)
        })

    return plugin.finish(items, update_listing=True)


@plugin.route('/sites/<cls>/shows/<showid>/<showpage>/episodes/<episodeid>/')
def get_episode_data(cls, showid, showpage, episodeid):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    items = [{
        'label': item['label'],
        'path': item['url'] + item['vid'],
        'is_playable': True} for item in api.get_episode_data(url)]
    return items




if __name__ == '__main__':
    try:
        plugin.run()
    except Exception, e:
        plugin.notify(msg=e)
