from xbmcswift2 import Plugin, xbmc, xbmcgui, xbmcaddon
import abc
from resources.lib.abc_base import BaseForum
from resources.lib.sites import *
import resources.lib.util as util
import resources.lib.errors as errors
import urlresolver


plugin = Plugin()

@plugin.route('/')
def index():
    items = [{
        'label': sc.long_name,
        'path': plugin.url_for('get_category_menu', siteid=index, cls=sc.__name__),
        'thumbnail': sc.thumbnail
        } for index, sc in enumerate(BaseForum.__subclasses__())]

    items.append({
        'label': 'Url Resolver Settings',
        'path': plugin.url_for('get_urlresolver_settings'),
        })
    return items


@plugin.route('/urlresolver/')
def get_urlresolver_settings():
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

    items = []

    # get frames
    f = api.get_frame_menu()
    if f:
        items = [{
            'label': item['label'],
            'path': plugin.url_for('browse_frame', siteid=siteid, cls=cls,
                frameid=index, url=item['url'])
        } for index, item in enumerate(f)]

    # get categories


    return items


@plugin.route('/sites/<cls>/frames/<frameid>/')
def browse_frame(cls, frameid):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    plugin.log.debug('browse frame: {frame}'.format(frame=url))

    items = [{
        'label': item['label'],
        'path': plugin.url_for('browse_episodes', siteid=siteid, cls=cls,
            frameid=frameid, showid=index, showpage=1, url=item['url'])
    } for index, item in enumerate(api.browse_frame(url))]

    return items


@plugin.route('/sites/<cls>/shows/<showid>/<showpage>/')
def browse_episodes(cls, showid, showpage=1):
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
            'path': plugin.url_for('browse_episodes', siteid=siteid,
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
