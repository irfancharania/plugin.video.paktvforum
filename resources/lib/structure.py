import resources.lib.util as util

class Category():
    def __init__(self, label, channels):
        self.label = label
        self.channels = channels


class Channel():
    def __init__(self, id, label, thumb=None):
        self.id = id
        self.label = label
        self.__thumb = thumb

    def get_thumb(self, default=None):
        if self.__thumb != None:
            result = self.__thumb
        else:
            result = default if default != None else ''

        return util.get_image_path(result)

