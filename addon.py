from xbmcswift2 import Plugin, xbmcgui
from resources.lib.abc_base import BaseForum
from resources.lib.sites import *
import resources.lib.util as util
from operator import itemgetter
import resources.lib.structure as s


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

    # check if site is available
    if api.base_url:
        available = util.is_site_available(api.base_url)

        if available:
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

        else:
            msg = [
                '[B][COLOR red]Website is unavailable.[/COLOR][/B]',
                '{site} is unavailable at this time'.format(
                    site=api.long_name),
                'Please try again later.']
            plugin.log.error(msg[0])

            dialog = xbmcgui.Dialog()
            dialog.ok(api.long_name, *msg)
    else:
        msg = 'Base url not implemented'
        plugin.log.error(msg)
        raise Exception(msg)


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

    # Some forum frames contain shows
    # while others contain episodes
    contents, contype = api.browse_frame(frameid, url)
    if contype and contype == s.ThreadType().Episode:
        items = [{
            'label': item['label'],
            'path': plugin.url_for(
                'get_episode_data', siteid=siteid, cls=cls, frameid=frameid,
                epid=item.get('pk', '0'), url=item['url'])
        } for item in contents]
    else:
        items = [{
            'label': item['label'],
            'path': plugin.url_for(
                'browse_shows', siteid=siteid, cls=cls, frameid=frameid,
                showid=item.get('pk', '0'), showpage=1, url=item['url'])
        } for item in contents]

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
                showid=showid, epid=item.get('pk', 0), url=item['url'])
        } for item in videos]

        if next_url:
            items.append({
                'label': 'Next >>',
                'path': plugin.url_for(
                    'browse_shows', siteid=siteid,
                    cls=cls, showid=showid, showpage=str(showpage + 1),
                    url=next_url)
            })
    else:
        msg = '[B][COLOR red]No episodes found.[/COLOR][/B]'
        plugin.log.error(msg)
        dialog = xbmcgui.Dialog()
        dialog.ok(api.long_name, msg)

    return items


@plugin.route('/sites/<cls>/episodes/e<epid>/')
def get_episode_data(cls, epid):
    siteid = int(plugin.request.args['siteid'][0])
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[int(siteid)]()

    plugin.log.debug('browse episode: {ep}'.format(ep=url))

    data = api.get_episode_data(url)
    if data:
        items = [{
            'label': item['label'],
            'path': plugin.url_for(
                'play_video', siteid=siteid, cls=cls,
                epid=epid, partnum=item['partnum'],
                media=item['media']),
            'is_playable': True
            } for item in data]
        return plugin.finish(items, sort_methods=['title'])
    else:
        msg = '[B][COLOR red]No valid links found.[/COLOR][/B]'
        plugin.log.error(msg)
        dialog = xbmcgui.Dialog()
        dialog.ok(api.long_name, msg)


@plugin.route('/sites/<cls>/episodes/e<epid>/<partnum>')
def play_video(cls, epid, partnum):
    siteid = int(plugin.request.args['siteid'][0])
    api = BaseForum.__subclasses__()[int(siteid)]()

    part_media = plugin.request.args['media'][0]
    media = []

    import urlresolver
    for host, vid in sorted(part_media, key=lambda x: x[0].server):
        r = urlresolver.HostedMediaFile(
            host=host.server, media_id=vid)
        if r:
            media.append(r)

    source = urlresolver.choose_source(media)
    print '>>> Source selected'
    print source

    if source:
        url = source.resolve()
        plugin.log.debug('play video: {url}'.format(url=url))

        plugin.set_resolved_url(url)

    else:
        msg = ['Unable to play video', 'Please choose another source']
        plugin.log.error(msg[0])
        dialog = xbmcgui.Dialog()
        dialog.ok(api.long_name, *msg)


if __name__ == '__main__':
    try:
        plugin.run()
    except Exception, e:
        plugin.log.error(e)
        plugin.notify(msg=e)
