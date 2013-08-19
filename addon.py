from xbmcswift2 import Plugin, xbmcgui
from resources.lib.abc_base import BaseForum
from resources.lib.sites import *
import resources.lib.util as util
from operator import itemgetter
import resources.lib.structure as s


bookmark_storage = 'my_bookmarks'
temp_storage = 'temp_storage'

plugin = Plugin()


@plugin.route('/')
def index():
    items = [{
        'label': '[B]Bookmarks[/B]',
        'path': plugin.url_for('show_bookmarks'),
        'thumbnail': util.get_image_path('bookmark.png')}]

    items.extend([{
        'label': sc.long_name,
        'path': plugin.url_for(
            'get_category_menu', siteid=index,
            cls=sc.__name__),
        'thumbnail': util.get_image_path(sc.local_thumb),
        'icon': util.get_image_path(sc.local_thumb),
        } for index, sc in enumerate(BaseForum.__subclasses__())])

    thumb = util.get_image_path('settings.png')
    items.append({
        'label': '[COLOR white]Url Resolver Settings[/COLOR]',
        'path': plugin.url_for('get_urlresolver_settings'),
        'thumbnail': thumb,
        'icon': thumb
        })
    return items


###############################################


@plugin.route('/bookmarks/')
def show_bookmarks():
    def context_menu(item_path):
        context_menu = [(
            'Remove Bookmark',
            'XBMC.RunPlugin(%s)' % plugin.url_for('remove_bookmark',
                                                  item_path=item_path,
                                                  refresh=True),
        )]
        return context_menu

    bookmarks = plugin.get_storage(bookmark_storage)
    items = bookmarks.values()

    for item in items:
        item['context_menu'] = context_menu(item['path'])
    if not items:
        items = [{
            'label': '- No Bookmarks -',
            'path': plugin.url_for('show_bookmarks'),
        }]

    return plugin.finish(items, sort_methods=['title'])


@plugin.route('/bookmarks/add/<item_path>')
def add_bookmark(item_path):
    bookmarks = plugin.get_storage(bookmark_storage)

    if not item_path in bookmarks:
        temp = plugin.get_storage(temp_storage)
        item = temp[item_path]

        groupname = plugin.request.args['groupname'][0]
        if groupname:
            item['label'] = groupname + ' - ' + item['label']

        bookmarks[item_path] = item
        bookmarks.sync()

    dialog = xbmcgui.Dialog()
    dialog.ok('Add Bookmark',
              'Successfully bookmarked: '
              '{label}'.format(label=item['label']))


@plugin.route('/bookmarks/remove/<item_path>')
def remove_bookmark(item_path):
    bookmarks = plugin.get_storage(bookmark_storage)
    label = bookmarks[item_path]['label']

    dialog = xbmcgui.Dialog()
    if dialog.yesno('Remove Bookmark',
                    'Are you sure you wish to remove bookmark:',
                    '{label}'.format(label=label)):

        plugin.log.debug('remove bookmark: {label}'.format(label=label))

        r = plugin.request.args.get('refresh', None)
        if r:
            refresh = bool(r[0])
        else:
            refresh = False

        if item_path in bookmarks:
            del bookmarks[item_path]
            bookmarks.sync()
            if refresh:
                xbmc.executebuiltin("Container.Refresh")


###############################################


def __add_listitem(items, groupname=''):
    bookmarks = plugin.get_storage(bookmark_storage)

    def context_menu(item_path, groupname):
        if not item_path in bookmarks:
            context_menu = [(
                'Add Bookmark',
                'XBMC.RunPlugin(%s)' % plugin.url_for(
                    endpoint='add_bookmark',
                    item_path=item_path,
                    groupname=groupname
                ),
            )]
        else:
            context_menu = [(
                'Remove Bookmark',
                'XBMC.RunPlugin(%s)' % plugin.url_for(
                    endpoint='remove_bookmark',
                    item_path=item_path
                ),
            )]
        return context_menu

    temp = plugin.get_storage(temp_storage)
    temp.clear()
    for item in items:
        temp[item['path']] = item
        item['context_menu'] = context_menu(item['path'], groupname)
    temp.sync()

    return items


###############################################


@plugin.route('/urlresolver/')
def get_urlresolver_settings():
    import urlresolver
    urlresolver.display_settings()
    return


@plugin.route('/sites/<siteid>-<cls>/')
def get_category_menu(siteid, cls):
    siteid = int(siteid)
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
            plugin.log.error(msg[1])

            dialog = xbmcgui.Dialog()
            dialog.ok(api.long_name, *msg)
    else:
        msg = 'Base url not implemented'
        plugin.log.error(msg)
        raise Exception(msg)


@plugin.route('/sites/<siteid>-<cls>/category/<categoryid>/')
def browse_category(siteid, cls, categoryid):
    siteid = int(siteid)
    api = BaseForum.__subclasses__()[siteid]()

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
    return __add_listitem(groupname=api.short_name,
                          items=sorted(items, key=by_label))


@plugin.route('/sites/<siteid>-<cls>/frames/f<frameid>/')
def browse_frame(siteid, cls, frameid):
    siteid = int(siteid)
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[siteid]()

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

    return __add_listitem(groupname=api.short_name, items=items)


@plugin.route('/sites/<siteid>-<cls>/channels/c<channelid>/')
def browse_channels(siteid, cls, channelid):
    siteid = int(siteid)
    api = BaseForum.__subclasses__()[siteid]()

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
    return __add_listitem(groupname=api.short_name, items=items)


@plugin.route('/sites/<siteid>-<cls>/shows/s<showid>/<showpage>/')
def browse_shows(siteid, cls, showid, showpage=1):
    siteid = int(siteid)
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[siteid]()

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

        return __add_listitem(groupname=api.short_name, items=items)
    else:
        msg = '[B][COLOR red]No episodes found.[/COLOR][/B]'
        plugin.log.error(msg)
        dialog = xbmcgui.Dialog()
        dialog.ok(api.long_name, msg)


@plugin.route('/sites/<siteid>-<cls>/episodes/e<epid>/')
def get_episode_data(siteid, cls, epid):
    siteid = int(siteid)
    url = plugin.request.args['url'][0]
    api = BaseForum.__subclasses__()[siteid]()

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


@plugin.route('/sites/<siteid>-<cls>/episodes/e<epid>/<partnum>')
def play_video(siteid, cls, epid, partnum):
    siteid = int(siteid)
    api = BaseForum.__subclasses__()[siteid]()

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
