import resources.lib.util as util


class ThreadType():
    ''' Enum representing types a forum can contain'''
    Show, Episode = range(2)


class Category():
    def __init__(self, label, channels):
        self.label = label
        self.channels = channels


class Channel():
    def __init__(self, id, label, thumb=''):
        self.id = id
        self.label = label
        self.__thumb = thumb

    @property
    def thumb(self):
        if self.__thumb:
            self.__thumb = util.get_image_path(self.__thumb)
        return self.__thumb
