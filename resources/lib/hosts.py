import resources.lib.util as util


class Host():
    def __init__(self, server, label, thumb=None):
        self.server = server,
        self.label = label,
        self.__thumb = thumb

    def get_thumb(self, default=None):
        if self.__thumb is not None:
            result = self.__thumb
        else:
            result = default if default is not None else ''

        return util.get_image_path(result)


''' Resolvable Hosts '''
dailymotion = Host('dailymotion.com', 'Daily Motion', 'dailymotion.png')
facebook = Host('facebook.com', 'Facebook', 'facebook.png')
hostingbulk = Host('hostingbulk.com', 'Hosting Bulk')
nowvideo = Host('nowvideo.eu', 'Now Video', 'nowvideo.png')
putlocker = Host('putlocker.com', 'PutLocker', 'putlocker.png')
tunepk = Host('tune.pk', 'Tune PK', 'tunepk.jpg')
videoweed = Host('videoweed.es', 'Video Weed', 'videoweed.jpg')
youtube = Host('youtube.com', 'Youtube', 'youtube.png')
