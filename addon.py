from xbmcswift2 import Plugin, xbmcgui
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
        'path': plugin.url_for(
            'get_category_menu', siteid=index,
            cls=sc.__name__),
        'thumbnail': util.get_image_path(sc.local_thumb),
        'icon': util.get_image_path(sc.local_thumb),
        } for index, sc in enumerate(BaseForum.__subclasses__())]

    thumb = util.get_image_path('settings.png')
    items.append({
        'label': '[COLOR white]Url Resolver Settings[/COLOR]',
        'path': plugin.url_for('get_urlresolver_settings'),
        'thumbnail': thumb,
        'icon': thumb
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
            'path': plugin.url_for(
                'browse_frame', siteid=siteid, cls=cls,
                frameid=index, url=item['url'])
        } for index, item in enumerate(f)]

    # get categories
    c = api.get_category_menu()
    if c:
        categoryitems = [{
            'label': '[B]{item}[/B]'.format(item=item['label']),
            'path': plugin.url_for(
                'browse_category', siteid=siteid, cls=cls,
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
        'label': item.label,
        'thumbnail': item.thumb,
        'icon': item.thumb,
        'path': plugin.url_for(
            'browse_channels', siteid=siteid, cls=cls,
            channelid=item.id)
    } for item in api.get_channel_menu(categoryid)]

    by_label = itemgetter('label')
    return sorted(items, key=by_label)


@plugin.route('/sites/<cls>/frames/f<frameid>/')
def browse_frame(cls, frameid):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    plugin.log.debug('browse frame: {frame}'.format(frame=url))

    items = [{
        'label': item['label'],
        'path': plugin.url_for(
            'browse_shows', siteid=siteid, cls=cls,
            frameid=frameid, showid=index, showpage=1, url=item['url'])
    } for index, item in enumerate(api.browse_frame(url))]

    return items


@plugin.route('/sites/<cls>/channels/c<channelid>/')
def browse_channels(cls, channelid):
    siteid = int(plugin.request.args['siteid'][0])
    api = BaseForum.__subclasses__()[int(siteid)]()

    plugin.log.debug('browse channel: {channel}'.format(channel=channelid))

    channels, shows = api.get_show_menu(channelid)

    showitems = [{
        'label': item['label'],
        'path': plugin.url_for(
            'browse_shows', siteid=siteid, cls=cls,
            showid=item['pk'], showpage=1, url=item['url'])
    } for item in shows]

    channelitems = [{
        'label': '[B]{item}[/B]'.format(item=item['label']),
        'path': plugin.url_for(
            'browse_channels', siteid=siteid, cls=cls,
            channelid=item['pk'], url=item['url'])
    } for item in channels]

    by_label = itemgetter('label')
    items = showitems + sorted(channelitems, key=by_label)
    return items


@plugin.route('/sites/<cls>/shows/s<showid>/<showpage>/')
def browse_shows(cls, showid, showpage=1):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    showpage = int(showpage)

    plugin.log.debug('browse show: {show}'.format(show=url))

    videos, next_url = api.get_episode_menu(url, showpage)

    items = []

    if videos:
        items = [{
            'label': item['label'],
            'path': plugin.url_for(
                'get_episode_data', siteid=siteid, cls=cls,
                showid=showid, epid=index, url=item['url'])
        } for index, item in enumerate(videos)]

        if next_url:
            items.append({
                'label': 'Next >>',
                'path': plugin.url_for(
                    'browse_shows', siteid=siteid,
                    cls=cls, showid=showid, showpage=str(showpage + 1),
                    url=next_url)
            })
    else:
        ## TODO: Pop up dialog: No episodes found.
        pass

    return items


@plugin.route('/sites/<cls>/shows/s<showid>/episodes/e<epid>/')
def get_episode_data(cls, showid, epid):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    items = [{
        'label': item['label'],
        'path': plugin.url_for(
            'play_video', siteid=siteid, cls=cls, showid=showid,
            epid=epid, partnum=item['partnum'], media=item['media']),
        'is_playable': True
        } for item in api.get_episode_data(url)]
    return plugin.finish(items, sort_methods=['title'])


@plugin.route('/sites/<cls>/shows/s<showid>/episodes/e<epid>/<partnum>')
def play_video(cls, showid, epid, partnum):
    part_media = plugin.request.args['media'][0]
    media = []

    print part_media

    import urlresolver
    for host, vid in sorted(part_media, key=lambda x: x[0].server):
        print '--'*22
        print host.server
        print vid
        r = urlresolver.HostedMediaFile(
            host=host.server, media_id=vid)
        if r:
            media.append(r)

    print '**::'*22
    print media
    print '**::'*22

    source = urlresolver.choose_source(media)
    print '----->>>>>> source'
    print source

    if source:
        print 'RESOLVING URL'
        url = source.resolve()
        print '----->>>>>> url'
        print url
        plugin.log.debug('play video: {url}'.format(url=url))

        plugin.set_resolved_url(url)

    else:
        msg = 'Unable to play video'
        plugin.log.error(msg)

        dialog = xbmcgui.Dialog()
        dialog.ok(msg, 'Please choose another source')

if __name__ == '__main__':
    try:
        plugin.run()
    except Exception, e:
        plugin.log.error(e)
        plugin.notify(msg=e)
