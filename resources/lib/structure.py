import resources.lib.util as util

class category():
    def __init__(self, label, channels):
        self.label = label
        self.channels = channels

class channel():
    def __init__(self, id, label, thumb=None):
        self.__id = id
        self.__label = label
        self.__thumb = thumb

    def get_id(self):
        return self.__id

    def get_label(self):
        return self.__label

    def get_thumb(self, default=None):
        result = ''
        if self.__thumb == None:
            if default != None:
                result = default
        else:
            result = util.get_image_path(self.__thumb)
        return result